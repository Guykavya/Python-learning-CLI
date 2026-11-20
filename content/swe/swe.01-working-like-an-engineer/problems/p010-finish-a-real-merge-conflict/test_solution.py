import shutil
import subprocess


def git(repo, *args, check=True):
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "init.defaultBranch=main",
         "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", *args],
        cwd=repo, capture_output=True, text=True, check=check)


def test_git_is_installed():
    assert shutil.which("git"), "git is not installed; swe.01 section 3 shows how to install it."



from pathlib import Path

import pytest

from solution import finish_merge

BASE = "TEA = 10\nCOFFEE = 20\nCAKE = 30\nJUICE = 40\n"


def make_conflict(tmp_path, files=("prices.py",)):
    repo = tmp_path / "shop"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "config", "commit.gpgsign", "false")
    for f in files:
        (repo / f).write_text(BASE, encoding="utf-8", newline="\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "Add prices")
    git(repo, "switch", "-q", "-c", "feature")
    for f in files:
        (repo / f).write_text(BASE.replace("CAKE = 30", "CAKE = 45"), encoding="utf-8", newline="\n")
    git(repo, "commit", "-qam", "Raise cake price (feature)")
    git(repo, "switch", "-q", "main")
    for f in files:
        (repo / f).write_text(BASE.replace("CAKE = 30", "CAKE = 35"), encoding="utf-8", newline="\n")
    git(repo, "commit", "-qam", "Raise cake price (main)")
    r = git(repo, "merge", "feature", check=False)
    assert r.returncode != 0, "The test setup should produce a merge conflict."
    assert (repo / ".git" / "MERGE_HEAD").exists()
    return repo


def parents(repo):
    return git(repo, "rev-list", "--parents", "-n", "1", "HEAD").stdout.split()[1:]


def test_resolves_and_commits(tmp_path):
    repo = make_conflict(tmp_path)
    final = "TEA = 10\nCOFFEE = 20\nCAKE = 40\nJUICE = 40\n"
    finish_merge(repo, "prices.py", final)
    assert git(repo, "status", "--porcelain").stdout == "", "After finishing, git status must be clean."
    assert len(parents(repo)) == 2, "The commit must be a merge commit with two parents (use git commit, not a new branch)."
    assert (repo / "prices.py").read_bytes() == final.encode(), "The file must contain exactly resolved_text."
    assert not (repo / ".git" / "MERGE_HEAD").exists(), "The merge must be finished (MERGE_HEAD gone)."
    assert "<<<<<<<" not in (repo / "prices.py").read_text(encoding="utf-8")


def test_accepts_str_or_path_for_repo(tmp_path):
    repo = make_conflict(tmp_path)
    finish_merge(str(repo), "prices.py", BASE)
    assert len(parents(repo)) == 2


def test_no_merge_in_progress(tmp_path):
    repo = tmp_path / "plain"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "a.txt").write_text("x\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "one")
    with pytest.raises(RuntimeError, match="no merge in progress"):
        finish_merge(repo, "a.txt", "y\n")
    assert (repo / "a.txt").read_text(encoding="utf-8") == "x\n", "Do not write anything when there is no merge."


def test_markers_left_in_the_text_are_refused_before_writing(tmp_path):
    repo = make_conflict(tmp_path)
    before = (repo / "prices.py").read_bytes()
    with pytest.raises(ValueError):
        finish_merge(repo, "prices.py", "<<<<<<< HEAD\nCAKE = 35\n=======\nCAKE = 45\n>>>>>>> feature\n")
    assert (repo / "prices.py").read_bytes() == before, "On ValueError the file must not be touched."
    assert (repo / ".git" / "MERGE_HEAD").exists(), "The merge must still be in progress."


def test_other_unmerged_files_stop_the_commit(tmp_path):
    repo = make_conflict(tmp_path, files=("prices.py", "drinks.py"))
    with pytest.raises(RuntimeError) as e:
        finish_merge(repo, "prices.py", BASE)
    assert "drinks.py" in str(e.value), "The error message must name the files that are still unmerged."
    assert (repo / ".git" / "MERGE_HEAD").exists(), "Do not commit while another file is unresolved."
    finish_merge(repo, "drinks.py", BASE)
    assert len(parents(repo)) == 2 and git(repo, "status", "--porcelain").stdout == ""
    assert (repo / "prices.py").read_text(encoding="utf-8") == BASE, "The first file keeps its resolution."


def test_line_endings_are_written_as_given(tmp_path):
    repo = make_conflict(tmp_path)
    finish_merge(repo, "prices.py", "TEA = 10\nCAKE = 40\n")
    assert b"\r" not in (repo / "prices.py").read_bytes(), "Write bytes: no newline translation."
