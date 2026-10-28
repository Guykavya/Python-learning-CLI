import pytest

from solution import read_text_lenient


def put(tmp_path, data):
    path = tmp_path / "t.txt"
    path.write_bytes(data)
    return path


def test_valid_utf8(tmp_path):
    path = put(tmp_path, "caf\u00e9 \u20b9".encode("utf-8"))
    assert read_text_lenient(path) == ("caf\u00e9 \u20b9", False), "Valid UTF-8 must be read as it is, with had_errors False."


def test_bad_byte_replaced(tmp_path):
    path = put(tmp_path, b"caf\xe9 ok")
    assert read_text_lenient(path) == ("caf\ufffd ok", True), "A bad byte becomes the replacement character (errors='replace'), and had_errors is True."


def test_two_bad_bytes(tmp_path):
    path = put(tmp_path, b"\xff\xfe")
    assert read_text_lenient(path) == ("\ufffd\ufffd", True), "Each bad byte gives one replacement character."


def test_good_text_kept_around_bad(tmp_path):
    path = put(tmp_path, b"line one\nbad \xe9\nline \xc3\xa9\n")
    text, bad = read_text_lenient(path)
    assert bad is True, "had_errors must be True for this file."
    assert text.startswith("line one\nbad ") and text.endswith("line \u00e9\n"), "The good parts, also the valid accent at the end, must be kept."


def test_empty_file(tmp_path):
    assert read_text_lenient(put(tmp_path, b"")) == ("", False), "An empty file is valid text."


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_text_lenient(tmp_path / "nope.txt")
