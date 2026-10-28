import builtins

import pytest

import solution
from solution import merge_lines, read_all


class SpyOpen:
    """Replaces open() inside the solution module and remembers every file object it returned."""

    def __init__(self):
        self.files = []

    def __call__(self, path, *args, **kwargs):
        f = builtins.open(path, *args, **kwargs)
        self.files.append(f)
        return f


@pytest.fixture
def spy(monkeypatch):
    s = SpyOpen()
    monkeypatch.setattr(solution, "open", s, raising=False)
    return s


@pytest.fixture
def three(tmp_path):
    paths = []
    for name, text in (("a.txt", "a1\na2\na3\n"), ("b.txt", "b1\nb2\n"), ("c.txt", "c1\nc2\nc3\nc4")):
        p = tmp_path / name
        p.write_text(text)
        paths.append(str(p))
    return paths


def test_read_all(three):
    assert read_all(three) == ["a1\na2\na3\n", "b1\nb2\n", "c1\nc2\nc3\nc4"], "read_all returns one string per path, in the order of the paths."


def test_read_all_empty_list():
    assert read_all([]) == [], "No paths: empty list (an ExitStack with nothing in it is fine)."


def test_merge_lines_stops_at_shortest(three):
    assert merge_lines(three) == [("a1", "b1", "c1"), ("a2", "b2", "c2")], "zip the open files together; strip the newline of each line; stop at the shortest file."


def test_all_files_are_closed_after_success(three, spy):
    read_all(three)
    assert len(spy.files) == 3, "Open every file with the name `open` (the tests watch it)."
    assert all(f.closed for f in spy.files), "Every file must be closed after read_all returns: register each with stack.enter_context(...) inside `with ExitStack() as stack:`."
    spy.files.clear()
    merge_lines(three)
    assert len(spy.files) == 3 and all(f.closed for f in spy.files), "merge_lines must close all its files too."


def test_all_opened_files_are_closed_when_a_later_open_fails(three, spy, tmp_path):
    paths = three[:2] + [str(tmp_path / "missing.txt")] + three[2:]
    with pytest.raises(FileNotFoundError):
        read_all(paths)
    assert len(spy.files) == 2, "The third open fails, so exactly two files were opened before it."
    assert all(f.closed for f in spy.files), "The two files that were already open must be closed when the third open fails: that is what ExitStack is for."
    spy.files.clear()
    with pytest.raises(FileNotFoundError):
        merge_lines(paths)
    assert all(f.closed for f in spy.files), "merge_lines must also close what it opened when a later path fails."


def test_all_files_open_at_the_same_time(three, spy):
    seen = []
    original = spy.__call__

    def watching(path, *a, **k):
        seen.append(sum(1 for f in spy.files if not f.closed))
        return original(path, *a, **k)

    solution.open = watching
    read_all(three)
    assert seen == [0, 1, 2], "All files are opened first and closed at the end: when opening the 2nd file, the 1st must still be open. Do not close each file right after reading it."


def test_uses_exitstack():
    import inspect
    src = inspect.getsource(solution)
    assert "ExitStack" in src, "Use contextlib.ExitStack: it lets you enter a number of context managers that is only known at run time."
