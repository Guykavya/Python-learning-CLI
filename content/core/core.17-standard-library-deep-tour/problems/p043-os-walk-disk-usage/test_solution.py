from pathlib import Path

import pytest

from solution import disk_usage, human_size, largest_files


def make(base: Path, rel: str, size: int):
    path = base / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    make(root, "a.txt", 100)
    make(root, "src/main.py", 300)
    make(root, "src/util/u.py", 50)
    make(root, ".git/objects", 5000)
    make(root, "src/__pycache__/main.pyc", 700)
    (root / "empty").mkdir()
    return root


def test_disk_usage_no_skip(project):
    usage = disk_usage(project)
    assert usage["."] == 6150, "The root '.' must hold the total of ALL files below it, sub-folders included."
    assert usage["src"] == 1050, "src = main.py + util/u.py + __pycache__/main.pyc: add every file to all its parent folders."
    assert usage["src/util"] == 50, "Keys use forward slashes ('src/util'), relative to root: use as_posix()."
    assert usage[".git"] == 5000, "Without skip, .git is a normal folder."


def test_disk_usage_keys(project):
    usage = disk_usage(project)
    assert set(usage) == {".", "src", "src/util", "src/__pycache__", ".git", "empty"}, (
        "Every folder must be a key (relative path, root is '.'); no absolute paths, no files."
    )
    assert usage["empty"] == 0, "An empty folder appears with 0 bytes."


def test_disk_usage_skip(project):
    usage = disk_usage(project, skip={".git", "__pycache__"})
    assert usage == {".": 450, "src": 350, "src/util": 50, "empty": 0}, (
        "Skipped folders must be pruned: change dirnames IN PLACE (dirnames[:] = ...) so os.walk never enters them, "
        "and do not count their files."
    )


def test_disk_usage_skip_nested_name(tmp_path):
    root = tmp_path / "r"
    make(root, "a/node_modules/big.js", 900)
    make(root, "a/keep.js", 10)
    usage = disk_usage(root, skip={"node_modules"})
    assert usage == {".": 10, "a": 10}, "skip matches folder NAMES at any depth, not only directly under root."


def test_disk_usage_is_dict_of_ints(project):
    usage = disk_usage(project)
    assert all(isinstance(v, int) for v in usage.values()), "Sizes are whole numbers of bytes (int)."


def test_largest_files(project):
    assert largest_files(project, 2, skip={".git"}) == [("src/__pycache__/main.pyc", 700), ("src/main.py", 300)], (
        "Biggest first, with relative posix paths."
    )
    assert largest_files(project, 3, skip={".git", "__pycache__"}) == [
        ("src/main.py", 300),
        ("a.txt", 100),
        ("src/util/u.py", 50),
    ], "Files inside skipped folders must not be listed."


def test_largest_files_ties_and_n(tmp_path):
    root = tmp_path / "t"
    make(root, "b.txt", 5)
    make(root, "a.txt", 5)
    make(root, "sub/c.txt", 5)
    make(root, "big.bin", 9)
    assert largest_files(root, 10) == [("big.bin", 9), ("a.txt", 5), ("b.txt", 5), ("sub/c.txt", 5)], (
        "Equal sizes are ordered by path; n larger than the number of files returns them all. Sort by (-size, path)."
    )
    assert largest_files(root, 0) == [], "n = 0 gives an empty list."


def test_human_size_bytes():
    assert human_size(0) == "0 B", "Below 1024, show the plain number of bytes with ' B'."
    assert human_size(1023) == "1023 B", "1023 is still below 1024: no conversion."


def test_human_size_units():
    assert human_size(1024) == "1.0 KiB", "1024 bytes is exactly 1.0 KiB (one decimal)."
    assert human_size(1536) == "1.5 KiB", "1536 / 1024 = 1.5."
    assert human_size(2 * 1024**2) == "2.0 MiB", "Keep dividing by 1024 while the value is 1024 or more."
    assert human_size(1024**3) == "1.0 GiB", "1024**3 bytes is 1.0 GiB."
    assert human_size(3 * 1024**4) == "3.0 TiB", "TiB is the biggest unit."
    assert human_size(2048 * 1024**4) == "2048.0 TiB", "Stop at TiB even if the value is above 1024."
