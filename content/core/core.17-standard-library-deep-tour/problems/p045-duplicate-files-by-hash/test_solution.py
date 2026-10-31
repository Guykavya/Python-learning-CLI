import hashlib
from pathlib import Path

import pytest

import solution
from solution import file_hash, find_duplicates, wasted_bytes


def make(base: Path, rel: str, data: bytes):
    path = base / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


@pytest.fixture
def root(tmp_path):
    r = tmp_path / "root"
    make(r, "a.txt", b"hello")
    make(r, "b.txt", b"hello")
    make(r, "c.txt", b"world")
    make(r, "notes/a.txt", b"hello")
    make(r, "big.bin", b"\x00" * 1000)
    return r


@pytest.fixture
def counted(monkeypatch):
    calls = []
    real = solution.file_hash

    def spy(path):
        calls.append(Path(path).name)
        return real(path)

    monkeypatch.setattr(solution, "file_hash", spy)
    return calls


def test_file_hash(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"abc" * 50_000)
    assert file_hash(p) == hashlib.sha256(b"abc" * 50_000).hexdigest(), "file_hash must be the sha256 hexdigest of the file's bytes (open in 'rb')."


def test_example(root):
    assert find_duplicates(root) == [["a.txt", "b.txt", "notes/a.txt"]], (
        "Same content = same hash. c.txt has the same size but different content; paths are relative with '/'."
    )


def test_only_shared_sizes_are_hashed(root, counted):
    find_duplicates(root)
    assert "big.bin" not in counted, "big.bin has a unique size: it cannot have a twin, so do not hash it. Group by size first."
    assert len(counted) == 4, f"Only the four 5-byte files need hashing; file_hash was called {len(counted)} times."


def test_no_duplicates(tmp_path, counted):
    r = tmp_path / "r"
    make(r, "one", b"1")
    make(r, "two", b"22")
    make(r, "three", b"333")
    assert find_duplicates(r) == [], "Three different sizes: no duplicates."
    assert counted == [], "All sizes are unique, so no file needs to be hashed at all."


def test_several_groups_sorted(tmp_path):
    r = tmp_path / "r"
    make(r, "z1.txt", b"zz")
    make(r, "z2.txt", b"zz")
    make(r, "m/b.txt", b"abc")
    make(r, "m/a.txt", b"abc")
    make(r, "a.txt", b"abd")
    groups = find_duplicates(r)
    assert groups == [["m/a.txt", "m/b.txt"], ["z1.txt", "z2.txt"]], (
        "Each group sorted, and the list of groups sorted. a.txt has the same size as m/*.txt but other bytes."
    )


def test_empty_files_ignored(tmp_path):
    r = tmp_path / "r"
    make(r, "e1", b"")
    make(r, "e2", b"")
    make(r, "d/e3", b"")
    assert find_duplicates(r) == [], "Empty files are ignored, even though their contents are equal."


def test_same_name_different_folders(tmp_path):
    r = tmp_path / "r"
    make(r, "x/report.txt", b"v1")
    make(r, "y/report.txt", b"v2")
    assert find_duplicates(r) == [], "The same NAME is not the same CONTENT: compare bytes (hashes), never names."


def test_wasted_bytes(root):
    groups = find_duplicates(root)
    assert wasted_bytes(root, groups) == 10, "One group of three 5-byte files: keep one, free 2 * 5 = 10 bytes."
    assert wasted_bytes(root, []) == 0, "No groups: nothing to free."


def test_wasted_bytes_two_groups(tmp_path):
    r = tmp_path / "r"
    make(r, "a", b"x" * 100)
    make(r, "b", b"x" * 100)
    make(r, "c", b"y" * 7)
    make(r, "d", b"y" * 7)
    make(r, "e", b"y" * 7)
    groups = find_duplicates(r)
    assert wasted_bytes(r, groups) == 100 + 14, "100 * (2 - 1) + 7 * (3 - 1) = 114."
