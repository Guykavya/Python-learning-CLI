import pytest

from solution import LineReader


def test_the_example():
    r = LineReader()
    assert r.feed(b"hel") == []
    assert r.feed(b"lo\r\nwor") == ["hello"], "The \\r\\n ends the line, and the \\r is not part of it."
    assert r.feed(b"ld\n\nx\n") == ["world", "", "x"], "The leftover 'wor' + 'ld' is one line; an empty line is ''."


def test_several_lines_in_one_chunk():
    assert LineReader().feed(b"a\nb\nc\n") == ["a", "b", "c"]


def test_no_newline_means_no_line():
    r = LineReader()
    assert r.feed(b"abc") == []
    assert r.feed(b"def") == []
    assert r.feed(b"\n") == ["abcdef"], "The leftover must wait for the next chunk."


def test_empty_feed():
    r = LineReader()
    assert r.feed(b"") == []
    assert r.feed(b"x\n") == ["x"]


def test_split_multibyte_character():
    data = "héllo wörld 😀\n".encode("utf-8")
    for cut in range(1, len(data)):
        r = LineReader()
        got = r.feed(data[:cut]) + r.feed(data[cut:])
        assert got == ["héllo wörld 😀"], (
            f"Cut at byte {cut}: decode only COMPLETE lines; a character can be split between two chunks.")


def test_one_byte_at_a_time():
    r = LineReader()
    out = []
    for b in b"ab\r\ncd\n":
        out += r.feed(bytes([b]))
    assert out == ["ab", "cd"]


def test_lone_carriage_return_inside_a_line_stays():
    assert LineReader().feed(b"a\rb\n") == ["a\rb"], "Only a \\r directly before \\n is part of the line ending."


def test_line_too_long():
    r = LineReader()
    with pytest.raises(ValueError):
        r.feed(b"x" * 65_537)


def test_long_but_finished_lines_are_fine():
    r = LineReader()
    got = r.feed((b"x" * 1000 + b"\n") * 100)
    assert len(got) == 100, "Only the unfinished line counts against the limit."


def test_long_line_in_pieces_is_caught():
    r = LineReader()
    with pytest.raises(ValueError):
        for _ in range(100):
            r.feed(b"y" * 1000)
