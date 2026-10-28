from solution import normalise_text_file


def run(tmp_path, data):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_bytes(data)
    count = normalise_text_file(src, dst)
    return count, dst.read_bytes(), src


def test_example(tmp_path):
    count, out, _ = run(tmp_path, b"\xef\xbb\xbfname\r\nZo\xc3\xab\r\nlast")
    assert out == b"name\nZo\xc3\xab\nlast", "Remove the BOM (read with utf-8-sig), turn \\r\\n into \\n, and keep the accent as UTF-8. Do not add a final newline."
    assert count == 3, "There are 3 lines."


def test_no_bom_lf_only(tmp_path):
    count, out, _ = run(tmp_path, b"a\nb\n")
    assert out == b"a\nb\n", "A clean file must stay exactly the same."
    assert count == 2, "Two lines."


def test_old_mac_endings(tmp_path):
    count, out, _ = run(tmp_path, b"a\rb\rc\r")
    assert out == b"a\nb\nc\n", "A single \\r is also a line ending. Text mode reading turns it into \\n."
    assert count == 3, "Three lines."


def test_mixed_endings(tmp_path):
    count, out, _ = run(tmp_path, b"1\r\n2\n3\r4")
    assert out == b"1\n2\n3\n4", "All three kinds of line ending become \\n."
    assert count == 4, "Four lines."


def test_output_has_no_bom_and_no_crlf(tmp_path):
    _, out, _ = run(tmp_path, b"\xef\xbb\xbfx\r\ny\r\n")
    assert not out.startswith(b"\xef\xbb\xbf"), "Write with encoding='utf-8', not 'utf-8-sig'. That would add a BOM."
    assert b"\r" not in out, "Open the output with newline='\\n' so no \\r is written."


def test_empty_file(tmp_path):
    count, out, _ = run(tmp_path, b"")
    assert (count, out) == (0, b""), "An empty file gives an empty file and 0 lines."


def test_source_unchanged(tmp_path):
    original = b"\xef\xbb\xbfq\r\n"
    _, _, src = run(tmp_path, original)
    assert src.read_bytes() == original, "Do not change the source file."
