import shutil
import subprocess

import pytest

from solution import is_ignored

P1 = ["*.pyc", "__pycache__/", "build/", ".env", "/todo.txt", "!keep.pyc"]
P2 = ["logs/*", "!logs/keep.txt", "docs/**/*.tmp", "/node_modules/", "**/cache/", "*.log", "!important.log"]
P3 = ["# a comment", "", "   ", "*.txt", "!a?.txt"]

CASES = [
    (P1, "a.pyc", True, "*.pyc matches at any depth, also at the top"),
    (P1, "src/pkg/a.pyc", True, "*.pyc has no slash: it matches the NAME at any depth"),
    (P1, "keep.pyc", False, "!keep.pyc re-includes it (last matching rule wins)"),
    (P1, "src/keep.pyc", False, "the re-include also works at depth"),
    (P1, "__pycache__/", True, "a directory named __pycache__"),
    (P1, "__pycache__", False, "a FILE named __pycache__: the trailing slash means directories only"),
    (P1, "src/__pycache__/x.txt", True, "inside an ignored directory"),
    (P1, "build/lib/a.py", True, "inside an ignored directory"),
    (P1, "docs/build/a.html", True, "build/ has no slash except the trailing one: it matches at any depth"),
    (P1, ".env", True, "a plain name"),
    (P1, "config/.env", True, "a plain name matches at any depth"),
    (P1, "todo.txt", True, "/todo.txt is anchored: it matches at the top"),
    (P1, "sub/todo.txt", False, "/todo.txt is anchored: it does not match in a sub folder"),
    (P1, "main.py", False, "nothing matches"),
    (P2, "logs/a.txt", True, "logs/* ignores things directly inside logs"),
    (P2, "logs/keep.txt", False, "re-included by the next line"),
    (P2, "logs/sub/x.txt", True, "logs/sub matches logs/*, so its content is ignored with it"),
    (P2, "docs/a.tmp", True, "** between slashes matches zero directories"),
    (P2, "docs/x/y/a.tmp", True, "** matches several directories"),
    (P2, "docs/a.txt", False, "not a .tmp file"),
    (P2, "node_modules/pkg/index.js", True, "/node_modules/ at the top"),
    (P2, "web/node_modules/x.js", False, "/node_modules/ is anchored to the top"),
    (P2, "a/b/cache/x.bin", True, "**/cache/ matches a cache directory anywhere"),
    (P2, "cache/", True, "**/ also matches zero directories"),
    (P2, "cache", False, "a file called cache; the pattern is for directories"),
    (P2, "error.log", True, "*.log"),
    (P2, "important.log", False, "!important.log"),
    (P2, "sub/important.log", False, "!important.log has no slash: any depth"),
    (P3, "notes.txt", True, "*.txt"),
    (P3, "ab.txt", False, "a?.txt re-includes ab.txt"),
    (P3, "abc.txt", True, "? matches exactly one character"),
    (P3, "src/ab.txt", False, "the re-include has no slash, so it works at depth"),
    (P3, "# a comment", False, "a comment line is not a pattern"),
]


@pytest.mark.parametrize("patterns,path,expected,why", CASES)
def test_case(patterns, path, expected, why):
    assert is_ignored(path, patterns) is expected, f"is_ignored({path!r}, {patterns}) should be {expected}: {why}."


def test_parent_directory_beats_a_negation():
    pats = ["build/", "!build/keep.txt"]
    assert is_ignored("build/keep.txt", pats) is True, (
        "If the parent directory is ignored, git never looks inside it: the ! rule cannot bring the file back.")


def test_order_matters_last_rule_wins():
    assert is_ignored("a.log", ["!a.log", "*.log"]) is True, "The ignore comes last, so it wins."
    assert is_ignored("a.log", ["*.log", "!a.log"]) is False


def test_returns_a_bool():
    assert is_ignored("x", []) is False


CHECK = [(P1, "src/pkg/a.pyc"), (P1, "keep.pyc"), (P1, "docs/build/a.html"), (P1, "sub/todo.txt"),
         (P2, "logs/keep.txt"), (P2, "docs/x/y/a.tmp"), (P2, "web/node_modules/x.js"), (P2, "important.log"),
         (P3, "ab.txt"), (P3, "abc.txt")]


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
@pytest.mark.parametrize("patterns,path", CHECK)
def test_agrees_with_real_git(tmp_path, patterns, path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / ".gitignore").write_text("\n".join(patterns) + "\n", encoding="utf-8")
    target = tmp_path / path
    if path.endswith("/"):
        target.mkdir(parents=True, exist_ok=True)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x", encoding="utf-8")
    r = subprocess.run(["git", "check-ignore", "--no-index", "-q", "--", path], cwd=tmp_path, capture_output=True)
    git_says = r.returncode == 0
    assert is_ignored(path, patterns) is git_says, f"git says ignored={git_says} for {path!r}; your function disagrees."
