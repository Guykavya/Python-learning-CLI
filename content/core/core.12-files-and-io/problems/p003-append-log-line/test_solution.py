from solution import append_line


def test_creates_file(tmp_path):
    p = tmp_path / "log.txt"
    append_line(p, "start")
    assert p.read_bytes() == b"start\n", "A missing file must be created. Mode 'a' does that."


def test_keeps_old_content(tmp_path):
    p = tmp_path / "log.txt"
    p.write_text("first\n")
    append_line(str(p), "second")
    assert p.read_bytes() == b"first\nsecond\n", "Old lines must stay. Mode 'w' wipes the file; use 'a'."


def test_many_appends(tmp_path):
    p = tmp_path / "log.txt"
    for i in range(5):
        append_line(p, f"line {i}")
    assert p.read_text().splitlines() == [f"line {i}" for i in range(5)], "Each call must add exactly one line, in order."


def test_utf8(tmp_path):
    p = tmp_path / "u.txt"
    append_line(p, "₹ café")
    assert p.read_bytes() == "₹ café\n".encode("utf-8"), "Use encoding='utf-8'."


def test_returns_none(tmp_path):
    assert append_line(tmp_path / "r.txt", "x") is None, "The function returns nothing."
