import io

from solution import first_lines


def test_basic(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("one\ntwo\nthree\nfour\n")
    assert first_lines(p, 2) == ["one", "two"], "Return the first two lines without the newline."


def test_fewer_lines(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("one\ntwo")
    assert first_lines(str(p), 5) == ["one", "two"], "If the file is short, return all lines (the last one has no newline)."


def test_zero(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("one\ntwo\n")
    assert first_lines(p, 0) == [], "n = 0 must give an empty list. Check n before you append."


def test_keeps_spaces(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("  indented  \nnext\n")
    assert first_lines(p, 1) == ["  indented  "], "Remove only the newline: use rstrip('\\n'), not strip()."


def test_big_file_is_not_read_whole(tmp_path, monkeypatch):
    p = tmp_path / "big.log"
    p.write_text("".join(f"row {i}\n" for i in range(50000)))
    assert first_lines(p, 3) == ["row 0", "row 1", "row 2"], "Big file: still the first three lines."

    calls = {"read": 0}
    real_open = io.open

    class Spy:
        def __init__(self, f):
            self._f = f

        def __iter__(self):
            return iter(self._f)

        def __next__(self):
            return next(self._f)

        def __enter__(self):
            self._f.__enter__()
            return self

        def __exit__(self, *a):
            return self._f.__exit__(*a)

        def read(self, *a):
            calls["read"] += 1
            return self._f.read(*a)

        def readlines(self, *a):
            calls["read"] += 1
            return self._f.readlines(*a)

        def readline(self, *a):
            return self._f.readline(*a)

        def close(self):
            return self._f.close()

        def __getattr__(self, name):
            return getattr(self._f, name)

    import builtins
    monkeypatch.setattr(builtins, "open", lambda *a, **k: Spy(real_open(*a, **k)))
    assert first_lines(p, 3) == ["row 0", "row 1", "row 2"], "Still the first three lines."
    assert calls["read"] == 0, "Do not call read() or readlines(): they load the whole file. Loop over the file instead."
