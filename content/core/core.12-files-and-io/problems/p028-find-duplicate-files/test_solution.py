from solution import find_duplicates


def make(root, files):
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def test_example(tmp_path):
    make(tmp_path, {"a.txt": b"hello", "sub/b.txt": b"hello", "c.txt": b"world", "sub/d.txt": b"hellp"})
    assert find_duplicates(tmp_path) == [["a.txt", "sub/b.txt"]], "a.txt and sub/b.txt are equal. c.txt and sub/d.txt have the same size but different bytes."


def test_no_duplicates(tmp_path):
    make(tmp_path, {"a": b"1", "b": b"22", "c": b"333"})
    assert find_duplicates(tmp_path) == [], "No two files are equal: return an empty list."


def test_empty_tree(tmp_path):
    assert find_duplicates(tmp_path) == [], "An empty folder has no duplicates."


def test_same_size_different_content(tmp_path):
    make(tmp_path, {"x.bin": b"abcd", "y.bin": b"abce"})
    assert find_duplicates(tmp_path) == [], "Same size is not enough. Compare a hash of the content."


def test_three_way_and_two_groups(tmp_path):
    make(tmp_path, {
        "one/a.dat": b"AAAA", "two/deep/a_copy.dat": b"AAAA", "a3.dat": b"AAAA",
        "m.txt": b"BB", "n/m.txt": b"BB", "z.txt": b"unique",
    })
    expected = [["a3.dat", "one/a.dat", "two/deep/a_copy.dat"], ["m.txt", "n/m.txt"]]
    assert find_duplicates(tmp_path) == expected, "Each group is sorted, and the list of groups is sorted. Use relative paths with '/'."


def test_empty_files_are_duplicates(tmp_path):
    make(tmp_path, {"e1": b"", "d/e2": b""})
    assert find_duplicates(tmp_path) == [["d/e2", "e1"]], "Two empty files have the same (empty) content. They are duplicates."


def test_folders_are_ignored(tmp_path):
    make(tmp_path, {"a/f.txt": b"same", "b/f.txt": b"same"})
    (tmp_path / "empty_dir").mkdir()
    assert find_duplicates(tmp_path) == [["a/f.txt", "b/f.txt"]], "Skip folders: only files are compared."


def test_returns_strings(tmp_path):
    make(tmp_path, {"p.txt": b"q", "r/p.txt": b"q"})
    result = find_duplicates(tmp_path)
    assert all(isinstance(name, str) for group in result for name in group), "Return relative paths as str (use .as_posix())."
