from solution import write_lines


def test_basic(tmp_path):
    p = tmp_path / "out.txt"
    n = write_lines(p, ["red", "green"])
    assert n == 2, "Return the number of lines written."
    assert p.read_bytes() == b"red\ngreen\n", "Each line must end with \\n, including the last one. write() does not add it for you."


def test_overwrites(tmp_path):
    p = tmp_path / "out.txt"
    p.write_text("old old old\nmore old\n")
    write_lines(str(p), ["new"])
    assert p.read_bytes() == b"new\n", "The old content must be gone. Use mode 'w', not 'a'."


def test_utf8(tmp_path):
    p = tmp_path / "u.txt"
    write_lines(p, ["café", "₹5"])
    assert p.read_bytes() == "café\n₹5\n".encode("utf-8"), "Write UTF-8 bytes: pass encoding='utf-8' to open()."


def test_empty_list(tmp_path):
    p = tmp_path / "e.txt"
    p.write_text("something")
    assert write_lines(p, []) == 0, "An empty list writes 0 lines."
    assert p.exists() and p.read_bytes() == b"", "An empty list must leave an empty file (and still wipe the old content)."


def test_data_is_flushed(tmp_path):
    p = tmp_path / "f.txt"
    write_lines(p, ["x"] * 5000)
    assert p.stat().st_size == 10000, "All the data must be on disk when the function returns. Close the file (use a with block)."
