import json
import os

import pytest

from solution import changes, snapshot

T0 = 1_700_000_000_000_000_000          # a fixed time in nanoseconds


def write(path, text, mtime_ns=T0):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    os.utime(path, ns=(mtime_ns, mtime_ns))


@pytest.fixture
def root(tmp_path):
    write(tmp_path / "a.txt", "1")
    write(tmp_path / "b.txt", "22")
    write(tmp_path / "sub" / "deep" / "c.txt", "333")
    return tmp_path


def test_snapshot_keys_and_values(root):
    snap = snapshot(root)
    assert snap == {"a.txt": (1, T0), "b.txt": (2, T0), "sub/deep/c.txt": (3, T0)}, \
        f"Relative paths with forward slashes -> (size, mtime_ns), files only (no folders). Got {snap}"


def test_snapshot_of_empty_folder(tmp_path):
    assert snapshot(tmp_path) == {}


def test_added_removed_modified(root):
    before = snapshot(root)
    write(root / "a.txt", "123456")
    (root / "b.txt").unlink()
    write(root / "sub" / "new.txt", "n")
    assert changes(before, snapshot(root)) == {"added": ["sub/new.txt"], "removed": ["b.txt"], "modified": ["a.txt"]}


def test_same_size_new_mtime_is_modified(root):
    before = snapshot(root)
    write(root / "a.txt", "9", mtime_ns=T0 + 500_000_000)       # half a second later, same size
    assert changes(before, snapshot(root))["modified"] == ["a.txt"], \
        "Same size, mtime 0.5 s later: use st_mtime_ns, whole seconds would miss it."


def test_untouched_file_is_not_modified(root):
    before = snapshot(root)
    write(root / "a.txt", "1")                                   # same bytes, same time
    assert changes(before, snapshot(root)) == {"added": [], "removed": [], "modified": []}, \
        "Nothing really changed: all three lists are empty."


def test_lists_are_sorted(root):
    before = snapshot(root)
    for name in ("z.txt", "m.txt", "b2.txt"):
        write(root / name, "x")
    assert changes(before, snapshot(root))["added"] == ["b2.txt", "m.txt", "z.txt"], "Sort each list."


def test_changes_works_on_saved_snapshots():
    old = json.loads('{"a.txt": [1, 5], "gone.txt": [2, 5]}')
    new = {"a.txt": [1, 5], "fresh.txt": [3, 6]}
    assert changes(old, new) == {"added": ["fresh.txt"], "removed": ["gone.txt"], "modified": []}, \
        "changes only compares two dictionaries (here loaded from JSON); it must not read the disk."
