from solution import parse_status

EMPTY = {"staged": [], "modified": [], "deleted": [], "untracked": []}


def test_empty_text_has_all_four_keys():
    assert parse_status("") == EMPTY, "Empty text: all four keys must exist, with empty lists."
    assert parse_status("\n\n") == EMPTY, "Blank lines are ignored."


def test_the_example():
    text = "M  a.py\n M b.py\nMM c.py\n?? d.py\nD  e.py\n D f.py\nA  g.py\nR  old.py -> new.py\n"
    assert parse_status(text) == {
        "staged": ["a.py", "c.py", "e.py", "g.py", "new.py"],
        "modified": ["b.py", "c.py"],
        "deleted": ["e.py", "f.py"],
        "untracked": ["d.py"],
    }


def test_unstaged_modification_keeps_its_leading_space():
    got = parse_status(" M b.py\n")
    assert got["staged"] == [], (
        "' M b.py' is NOT staged: X (the first character) is a space. Do not strip the whole line.")
    assert got["modified"] == ["b.py"]


def test_untracked_is_not_staged():
    got = parse_status("?? notes.txt\n")
    assert got == {**EMPTY, "untracked": ["notes.txt"]}, "'??' means untracked only: not staged, not modified."


def test_one_file_in_several_lists():
    got = parse_status("MM c.py\nD  e.py\n")
    assert got["staged"] == ["c.py", "e.py"] and got["modified"] == ["c.py"] and got["deleted"] == ["e.py"], (
        "MM is staged AND modified; 'D ' is staged AND deleted.")


def test_rename_uses_new_path_and_quotes_are_removed():
    got = parse_status('R  old name.py -> "new name.py"\n?? "my file.txt"\n')
    assert got["staged"] == ["new name.py"], "A rename lists the NEW path; quotes around it are removed."
    assert got["untracked"] == ["my file.txt"], "Remove the double quotes git puts around names with spaces."


def test_order_is_the_order_of_the_lines():
    got = parse_status("A  z.py\nA  b.py\nM  m.py\n")
    assert got["staged"] == ["z.py", "b.py", "m.py"], "Keep the order of the input; do not sort."
