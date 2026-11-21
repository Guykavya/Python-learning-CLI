import hashlib
import os

import pytest

import solution
from solution import find_duplicates, sha256_of


@pytest.fixture
def tree(tmp_path):
    files = {"notes.txt": b"my notes", "copy/notes.bak": b"my notes", "other.txt": b"my nodes",
             "big.bin": b"something longer", "empty1": b"", "empty2": b"",
             "a/b/deep.dat": b"something longer", "unique.txt": b"only one of me!!!!!"}
    for name, data in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return tmp_path


def names(groups, root):
    return [[p.relative_to(root).as_posix() for p in g] for g in groups]


def test_sha256_matches_hashlib_with_tiny_chunks(tmp_path):
    p = tmp_path / "f.bin"
    data = bytes(range(256)) * 10
    p.write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    assert sha256_of(p) == expected, "Return the hexdigest() of the file's bytes."
    assert sha256_of(p, chunk=7) == expected, "With chunk=7 the file is read in many small blocks: update the hash with every block."


def test_sha256_of_empty_file(tmp_path):
    p = tmp_path / "empty"
    p.write_bytes(b"")
    assert sha256_of(p) == hashlib.sha256(b"").hexdigest(), "An empty file has a hash too; the loop must simply end at once."


def test_groups_by_content_recursively(tree):
    assert names(find_duplicates(tree), tree) == [["a/b/deep.dat", "big.bin"], ["copy/notes.bak", "notes.txt"]], \
        "Content decides, not names; look in subfolders (rglob); sort each group and the list of groups."


def test_same_size_different_bytes_is_not_a_duplicate(tree):
    flat = [p.name for g in find_duplicates(tree) for p in g]
    assert "other.txt" not in flat, "'my nodes' has the same size as 'my notes' but different bytes: the hash must decide."


def test_empty_files_ignored_by_default(tree):
    flat = [p.name for g in find_duplicates(tree) for p in g]
    assert "empty1" not in flat, "min_size=1 by default: empty files are ignored."
    assert ["empty1", "empty2"] in names(find_duplicates(tree, min_size=0), tree), "With min_size=0 the two empty files are a group."


def test_min_size_filters(tree):
    assert names(find_duplicates(tree, min_size=10), tree) == [["a/b/deep.dat", "big.bin"]], \
        "'my notes' is 8 bytes, below min_size=10."


def test_only_shared_sizes_are_hashed(tree, monkeypatch):
    calls = []
    real = solution.sha256_of

    def counting(path, *args, **kwargs):
        calls.append(path.name)
        return real(path, *args, **kwargs)

    monkeypatch.setattr(solution, "sha256_of", counting)
    find_duplicates(tree)
    assert "unique.txt" not in calls, "unique.txt has a size nobody else has: it can have no duplicate, so do not read it."
    assert sorted(calls) == ["big.bin", "deep.dat", "notes.bak", "notes.txt", "other.txt"], \
        f"Hash only files whose size is shared (and call sha256_of for them). Hashed: {sorted(calls)}"


def test_no_duplicates(tmp_path):
    (tmp_path / "a").write_bytes(b"1")
    (tmp_path / "b").write_bytes(b"22")
    assert find_duplicates(tmp_path) == []


@pytest.mark.skipif(os.name == "nt", reason="creating symlinks needs extra rights on Windows")
def test_symlinks_are_skipped(tmp_path):
    (tmp_path / "real.txt").write_bytes(b"content")
    (tmp_path / "link.txt").symlink_to(tmp_path / "real.txt")
    assert find_duplicates(tmp_path) == [], "A symlink is not a second copy of the file: skip it with is_symlink()."
