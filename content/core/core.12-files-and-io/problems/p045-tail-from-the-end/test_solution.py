import builtins

from solution import tail_lines


class Count:
    """Wraps a real file and counts how many bytes read() returned."""

    total = 0

    def __init__(self, real):
        self._real = real

    def __enter__(self):
        self._real.__enter__()
        return self

    def __exit__(self, *exc):
        return self._real.__exit__(*exc)

    def read(self, *args):
        data = self._real.read(*args)
        Count.total += len(data)
        return data

    def __getattr__(self, name):
        return getattr(self._real, name)


def put(tmp_path, data):
    path = tmp_path / "log.txt"
    path.write_bytes(data)
    return path


def test_example(tmp_path):
    path = put(tmp_path, b"one\ntwo\nthree\nfour\n")
    assert tail_lines(path, 2) == ["three", "four"], "Return the last two lines without their newline."


def test_fewer_lines_than_n(tmp_path):
    path = put(tmp_path, b"a\nb\n")
    assert tail_lines(path, 10) == ["a", "b"], "If the file is shorter than n lines, return all lines. Stop at position 0."


def test_empty_file_and_zero(tmp_path):
    assert tail_lines(put(tmp_path, b""), 5) == [], "An empty file has no lines."
    assert tail_lines(put(tmp_path, b"a\n"), 0) == [], "n = 0 gives an empty list."


def test_no_final_newline(tmp_path):
    path = put(tmp_path, b"a\nb\nlast")
    assert tail_lines(path, 2) == ["b", "last"], "The last line has no newline. It is still a line."


def test_final_newline_is_not_an_extra_line(tmp_path):
    path = put(tmp_path, b"a\nb\n")
    assert tail_lines(path, 1) == ["b"], "A final newline ends the last line. It does not start an empty line."


def test_empty_lines_are_real_lines(tmp_path):
    path = put(tmp_path, b"a\n\nb\n\n")
    assert tail_lines(path, 3) == ["", "b", ""], "Empty lines count as lines."


def test_crlf(tmp_path):
    path = put(tmp_path, b"a\r\nb\r\nc\r\n")
    assert tail_lines(path, 2) == ["b", "c"], "Remove \\r\\n at the end of each line."


def test_tiny_blocks(tmp_path):
    text = "".join(f"line {i}\n" for i in range(40))
    path = put(tmp_path, text.encode())
    for size in (1, 2, 3, 5, 7, 50):
        assert tail_lines(path, 4, block_size=size) == ["line 36", "line 37", "line 38", "line 39"], f"block_size={size} must give the same result. Put each new block in front of the old data."


def test_multibyte_characters_cut_by_blocks(tmp_path):
    lines = ["\u20b9 rupee", "caf\u00e9", "\u4f60\u597d", "end"]
    path = put(tmp_path, ("\n".join(lines) + "\n").encode("utf-8"))
    for size in (1, 2, 3, 4, 5):
        assert tail_lines(path, 4, block_size=size) == lines, f"block_size={size}: decode after you have joined the bytes, not block by block."


def test_big_file_is_not_read_from_the_start(tmp_path, monkeypatch):
    text = "".join(f"2024-01-01 12:00:00 INFO event number {i:07d}\n" for i in range(40000))
    path = put(tmp_path, text.encode())
    assert path.stat().st_size > 1_500_000, "Test setup: the file should be big."
    real_open = builtins.open
    Count.total = 0
    monkeypatch.setattr(builtins, "open", lambda *a, **k: Count(real_open(*a, **k)))
    result = tail_lines(path, 3)
    monkeypatch.undo()
    assert result == [f"2024-01-01 12:00:00 INFO event number {i:07d}" for i in (39997, 39998, 39999)], "Wrong last lines for the big file."
    assert Count.total < 100_000, "You read too much of the file. Read blocks from the end, and stop when you have more than n newlines."
