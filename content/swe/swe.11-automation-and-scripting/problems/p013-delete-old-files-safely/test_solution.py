import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import solution
from solution import delete_older_than, refuse_dangerous_root

NOW = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)


def make(path, age):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
    t = (NOW - age).timestamp()
    os.utime(path, (t, t))
    return path


@pytest.fixture
def root(tmp_path):
    r = tmp_path / "logs"
    make(r / "old.log", timedelta(days=40))
    make(r / "new.log", timedelta(days=1))
    make(r / "sub" / "old2.tmp", timedelta(days=90))
    make(r / "exactly30.log", timedelta(days=30))
    make(r / "just-over.log", timedelta(days=30, seconds=1))
    return r


def rel(paths, base):
    return [Path(p).resolve().relative_to(base.resolve()).as_posix() for p in paths]


def test_dry_run_is_the_default(root):
    found = delete_older_than(root, 30, NOW)
    assert rel(found, root) == ["just-over.log", "old.log", "sub/old2.tmp"], \
        f"Old files, recursively, sorted. Exactly 30 days is NOT older than 30 days. Got {rel(found, root)}"
    for name in ("old.log", "sub/old2.tmp", "just-over.log"):
        assert (root / name).exists(), "dry_run=True is the default: nothing may be deleted."


def test_real_run_deletes_only_old_files(root):
    deleted = delete_older_than(root, 30, NOW, dry_run=False)
    assert rel(deleted, root) == ["just-over.log", "old.log", "sub/old2.tmp"]
    assert not (root / "old.log").exists() and not (root / "sub" / "old2.tmp").exists()
    assert (root / "new.log").exists() and (root / "exactly30.log").exists(), "Young files and the boundary file stay."
    assert (root / "sub").is_dir(), "Delete files only, never folders."


def test_now_is_injected(root):
    later = NOW + timedelta(days=100)
    found = delete_older_than(root, 30, later)
    assert len(found) == 5, "Use the `now` you are given, not the clock: 100 days later every file is old."
    assert delete_older_than(root, 365, NOW) == [], "Nothing is a year old."


def test_negative_days(root):
    with pytest.raises(ValueError):
        delete_older_than(root, -1, NOW)


def test_refuses_missing_folder_and_files(tmp_path):
    with pytest.raises(ValueError):
        refuse_dangerous_root(tmp_path / "nope")
    f = tmp_path / "f.txt"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        refuse_dangerous_root(f)


def test_refuses_the_top_of_the_file_system(tmp_path):
    with pytest.raises(ValueError):
        refuse_dangerous_root(Path(tmp_path.anchor))
    assert refuse_dangerous_root(tmp_path) == tmp_path.resolve(), "A normal folder is returned, resolved."


def test_refuses_the_home_folder(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    old = make(fake_home / "ancient.txt", timedelta(days=999))
    monkeypatch.setattr(solution.Path, "home", classmethod(lambda cls: fake_home))
    with pytest.raises(ValueError):
        refuse_dangerous_root(fake_home)
    with pytest.raises(ValueError):
        delete_older_than(fake_home, 30, NOW, dry_run=False)
    assert old.exists(), "Cleaning the home folder must be refused before anything is deleted."


def test_the_root_is_checked_first(root, monkeypatch):
    class Refused(Exception):
        pass

    def refuse(r):
        raise Refused()

    monkeypatch.setattr(solution, "refuse_dangerous_root", refuse)
    with pytest.raises(Refused):
        delete_older_than(root, 30, NOW, dry_run=False)
    assert (root / "old.log").exists(), "Call refuse_dangerous_root(root) FIRST, before touching any file."


@pytest.mark.skipif(os.name == "nt", reason="creating symlinks needs extra rights on Windows")
def test_symlinks_are_never_followed(tmp_path):
    outside = tmp_path / "precious"
    keep = make(outside / "thesis.docx", timedelta(days=400))
    root = tmp_path / "cache"
    make(root / "stale.tmp", timedelta(days=400))
    (root / "link-to-file").symlink_to(keep)
    (root / "link-to-folder").symlink_to(outside, target_is_directory=True)
    deleted = delete_older_than(root, 30, NOW, dry_run=False)
    assert rel(deleted, root) == ["stale.tmp"], f"Only the real file inside root; got {rel(deleted, root)}"
    assert keep.exists(), "A symlink must never lead the cleanup outside the folder."
    assert (root / "link-to-file").is_symlink(), "Skip symlinks entirely (do not delete the link either)."
