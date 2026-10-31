from solution import list_by_suffix


def make(tmp_path, names, folders=()):
    for n in names:
        (tmp_path / n).write_text("x")
    for d in folders:
        (tmp_path / d).mkdir()


def test_basic(tmp_path):
    make(tmp_path, ["b.txt", "a.TXT", "c.csv", "x.txt.bak"], ["notes"])
    assert list_by_suffix(tmp_path, ".txt") == ["a.TXT", "b.txt"], "Expected ['a.TXT', 'b.txt']: sorted, case-insensitive, only the last suffix."


def test_str_folder(tmp_path):
    make(tmp_path, ["a.py"])
    assert list_by_suffix(str(tmp_path), ".py") == ["a.py"], "A str folder must work too: wrap it in Path()."


def test_folders_are_skipped(tmp_path):
    make(tmp_path, ["real.txt"], ["data.txt"])
    assert list_by_suffix(tmp_path, ".txt") == ["real.txt"], "A folder named data.txt is not a file. Check is_file()."


def test_no_subfolders(tmp_path):
    make(tmp_path, ["top.txt"], ["sub"])
    (tmp_path / "sub" / "deep.txt").write_text("x")
    assert list_by_suffix(tmp_path, ".txt") == ["top.txt"], "Do not look inside sub-folders (no rglob)."


def test_sorted_names_not_paths(tmp_path):
    make(tmp_path, ["z.md", "m.md", "a.md", "b.MD"])
    result = list_by_suffix(tmp_path, ".md")
    assert result == ["a.md", "b.MD", "m.md", "z.md"], "Return sorted names (strings), not paths."
    assert all(isinstance(x, str) for x in result), "Names must be str: use item.name."


def test_empty(tmp_path):
    assert list_by_suffix(tmp_path, ".txt") == [], "No matches gives an empty list."
