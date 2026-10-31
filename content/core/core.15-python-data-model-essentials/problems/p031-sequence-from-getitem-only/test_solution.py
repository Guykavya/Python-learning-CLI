import pytest

from solution import Backwards, Multiples


def test_getitem_values():
    m = Multiples(3, 4)
    assert [m[0], m[1], m[2], m[3]] == [3, 6, 9, 12], "m[i] is step * (i + 1): the first multiple is step itself."


def test_getitem_out_of_range_raises_indexerror():
    m = Multiples(2, 3)
    with pytest.raises(IndexError):
        m[3]
    with pytest.raises(IndexError):
        m[-1]
    with pytest.raises(TypeError):
        m["a"]
    assert m[2] == 6, "The last valid index is count - 1."


def test_no_iter_and_no_len_defined():
    assert "__iter__" not in vars(Multiples), "The point of this problem: do NOT define __iter__. Python falls back to calling __getitem__(0), (1), ... until IndexError."
    assert "__len__" not in vars(Multiples), "Multiples must not define __len__ either."
    with pytest.raises(TypeError):
        len(Multiples(1, 3))


def test_for_loop_and_list_use_the_old_protocol():
    assert list(Multiples(5, 3)) == [5, 10, 15], "list() calls iter(), which falls back to __getitem__ with 0, 1, 2 ... It stops when IndexError is raised, so __getitem__ MUST raise IndexError past the end."
    assert [x for x in Multiples(1, 0)] == [], "count=0 gives an empty sequence."
    total = 0
    for x in Multiples(2, 4):
        total += x
    assert total == 20, "A for loop works with only __getitem__."


def test_in_and_builtins_work_too():
    m = Multiples(4, 5)
    assert 12 in m and 13 not in m, "`in` also falls back to iterating with __getitem__."
    assert sum(m) == 60 and max(m) == 20 and min(m) == 4, "sum/max/min iterate through the fallback."
    assert list(zip(m, "ab")) == [(4, "a"), (8, "b")], "zip iterates lazily with the same protocol."


def test_every_loop_starts_again():
    m = Multiples(1, 3)
    assert list(m) == list(m) == [1, 2, 3], "Each iter(m) starts at index 0 again, because the fallback iterator keeps its own counter."


def test_backwards_needs_len_and_getitem():
    b = Backwards([1, 2, 3, 4])
    assert len(b) == 4, "Backwards.__len__ is len of the wrapped sequence."
    assert [b[0], b[1], b[3]] == [4, 3, 1], "b[0] is the LAST item of the wrapped sequence."
    assert list(b) == [4, 3, 2, 1], "Iteration through __getitem__ gives the reversed order."


def test_backwards_errors():
    b = Backwards("abc")
    with pytest.raises(IndexError):
        b[3]
    with pytest.raises(IndexError):
        b[-1]
    assert "".join(b) == "cba", "Works with any sequence, such as a string."


def test_reversed_uses_len_and_getitem():
    b = Backwards([1, 2, 3])
    assert list(reversed(b)) == [1, 2, 3], "reversed() works on any object with __len__ and __getitem__: it calls b[len-1], b[len-2] ... b[0]."
    assert list(Backwards(Backwards("xyz"))) == list("xyz"), "Backwards of Backwards of 'xyz' is 'xyz' again: Backwards must accept another Backwards (it only needs len() and [])."


def test_multiples_cannot_be_reversed():
    with pytest.raises(TypeError):
        reversed(Multiples(2, 3))
