import pytest

from solution import Playlist


def test_len():
    assert len(Playlist(["a", "b", "c"])) == 3, "len(p) should be the number of songs. Define __len__."
    assert len(Playlist([])) == 0, "An empty playlist has length 0."


def test_getitem():
    p = Playlist(["Intro", "Main", "Outro"])
    assert p[0] == "Intro" and p[1] == "Main", "p[i] should return the i-th song. Define __getitem__."
    assert p[-1] == "Outro" and p[-3] == "Intro", "Negative indexes count from the end."


def test_index_error():
    p = Playlist(["a", "b"])
    with pytest.raises(IndexError):
        p[2]
    with pytest.raises(IndexError):
        p[-3]


def test_for_loop_and_list():
    p = Playlist(["a", "b", "c"])
    assert [s for s in p] == ["a", "b", "c"], "A for loop works with __getitem__ alone: it stops at IndexError."
    assert list(p) == ["a", "b", "c"], "list(p) uses the same protocol."


def test_in_and_bool_and_reversed():
    p = Playlist(["a", "b", "c"])
    assert "b" in p and "z" not in p, "`in` falls back to iterating with __getitem__."
    assert bool(p) is True and bool(Playlist([])) is False, "bool() falls back to __len__ (0 is falsy)."
    assert list(reversed(p)) == ["c", "b", "a"], "reversed() works when __len__ and __getitem__ exist."


def test_accepts_generator_and_copies():
    p = Playlist(s for s in ["x", "y"])
    assert list(p) == ["x", "y"] and list(p) == ["x", "y"], "Copy the input into a list so the playlist can be read twice (a generator is used up after one pass)."
    src = ["a"]
    q = Playlist(src)
    src.append("b")
    assert len(q) == 1, "Copy the input list; later changes to the original must not leak in."
