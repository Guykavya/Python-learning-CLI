import pytest

from solution import last_n, tail


def test_last_n_list():
    assert last_n(["a", "b", "c", "d"], 2) == ["c", "d"], "Keep the LAST n items, oldest first."
    assert last_n(["a"], 5) == ["a"], "Fewer items than n: return all of them."
    assert last_n([], 3) == [], "Nothing in, nothing out."


def test_last_n_zero_and_negative():
    assert last_n(["a", "b"], 0) == [], "n = 0 asks for no items."
    with pytest.raises(ValueError):
        last_n(["a", "b"], -1)


def test_last_n_returns_list():
    got = last_n(["x", "y"], 2)
    assert type(got) is list, "Return a list, not the deque itself: list(deque(...))."


class OnePass:
    """An iterable that may be walked only once and tracks how far it got."""

    def __init__(self, count):
        self.count = count
        self.used = False

    def __iter__(self):
        assert not self.used, "last_n walked the input twice. Read it once: a file or generator cannot be rewound."
        self.used = True
        for i in range(self.count):
            yield f"line {i}"


def test_last_n_one_pass_generator():
    gen = (c for c in "hello")
    assert last_n(gen, 3) == ["l", "l", "o"], "A generator works too: deque(gen, maxlen=n) reads it once."
    src = OnePass(100_000)
    assert last_n(src, 2) == ["line 99998", "line 99999"], "The last two of 100,000 lines."


def test_last_n_many_items():
    def gen():
        for i in range(1000):
            yield str(i)

    got = last_n(gen(), 3)
    assert got == ["997", "998", "999"], "Only the newest 3 survive: a deque with maxlen drops from the left when full."


def test_tail_unix_endings(tmp_path):
    p = tmp_path / "app.log"
    p.write_bytes(b"start\nload\nrun\nstop\n")
    assert tail(p, 2) == ["run", "stop"], "Return the lines without the trailing newline: line.rstrip('\\n')."


def test_tail_windows_endings(tmp_path):
    p = tmp_path / "win.log"
    p.write_bytes(b"one\r\ntwo\r\nthree\r\n")
    got = tail(p, 2)
    assert got == ["two", "three"], (
        "Windows files end lines with \\r\\n. Open in text mode (not 'rb'), which turns \\r\\n into \\n; "
        "then strip the \\n."
    )


def test_tail_no_final_newline(tmp_path):
    p = tmp_path / "x.txt"
    p.write_bytes(b"a\nb\nc")
    assert tail(p, 2) == ["b", "c"], "The last line has no newline but it is still a line."


def test_tail_keeps_other_whitespace(tmp_path):
    p = tmp_path / "x.txt"
    p.write_bytes(b"  indented\nend  \n\n")
    assert tail(p, 3) == ["  indented", "end  ", ""], (
        "Only remove the line ending. strip() would also eat the spaces, and the empty last line is a real line."
    )


def test_tail_default_and_utf8(tmp_path):
    p = tmp_path / "u.txt"
    p.write_bytes("\n".join(f"zeile {i} ü€" for i in range(25)).encode("utf-8"))
    got = tail(p)
    assert len(got) == 10, "The default n is 10."
    assert got[-1] == "zeile 24 ü€", "Open the file with encoding='utf-8', or non-ASCII text breaks on Windows."


def test_tail_accepts_str_path(tmp_path):
    p = tmp_path / "s.txt"
    p.write_bytes(b"1\n2\n3\n")
    assert tail(str(p), 1) == ["3"], "path may be a str as well as a Path."
