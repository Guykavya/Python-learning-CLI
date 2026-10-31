import pytest

from solution import RingBuffer


def make(cap, *items):
    rb = RingBuffer(cap)
    for x in items:
        rb.append(x)
    return rb


def test_bad_capacity():
    for bad in (0, -3):
        with pytest.raises(ValueError):
            RingBuffer(bad)
    # no assert message possible inside raises; this one is checked again below
    assert RingBuffer(1).capacity == 1, "capacity=1 is allowed and must be stored in .capacity."


def test_len_grows_then_stops_at_capacity():
    rb = RingBuffer(3)
    assert len(rb) == 0, "len() of an empty buffer is 0: define __len__ to return the number of stored items."
    rb.append("a")
    rb.append("b")
    assert len(rb) == 2, "len() is the number of items stored so far, not the capacity."
    rb.append("c")
    rb.append("d")
    rb.append("e")
    assert len(rb) == 3, "A full buffer overwrites the oldest item, so len() never goes above capacity."


def test_iteration_is_oldest_to_newest():
    rb = make(3, 1, 2)
    assert list(rb) == [1, 2], "Iterate from the oldest to the newest item (define __iter__)."
    rb = make(3, 1, 2, 3, 4, 5)
    assert list(rb) == [3, 4, 5], "After wrapping around, the oldest item is the one after the last overwritten slot. Iterate oldest first."
    rb.append(6)
    assert list(rb) == [4, 5, 6], "Each append to a full buffer drops the oldest and keeps the order."


def test_getitem_positive_and_negative():
    rb = make(3, "a", "b", "c", "d")          # holds b, c, d
    assert rb[0] == "b", "rb[0] is the OLDEST item (physical slot 0 is not necessarily the oldest after wrapping)."
    assert rb[2] == "d", "rb[len-1] is the newest item."
    assert rb[-1] == "d", "Negative indices count from the newest end: add len(self) to a negative index."
    assert rb[-3] == "b", "rb[-len] is the oldest item."


def test_getitem_errors():
    rb = make(3, 1, 2)
    with pytest.raises(IndexError):
        rb[2]
    with pytest.raises(IndexError):
        rb[-3]
    with pytest.raises(TypeError):
        rb["x"]
    with pytest.raises(IndexError):
        RingBuffer(2)[0]
    assert rb[1] == 2, "Valid indices are 0 .. len-1 (the number of STORED items, not the capacity)."


def test_unfilled_slots_are_not_visible():
    rb = make(5, "x")
    assert list(rb) == ["x"], "Do not yield the empty slots of a half-full buffer."
    with pytest.raises(IndexError):
        rb[1]


def test_is_full():
    rb = make(2, 1)
    assert rb.is_full() is False, "is_full() is False while len < capacity."
    rb.append(2)
    assert rb.is_full() is True, "is_full() is True once len == capacity, and stays True after wrapping."
    rb.append(3)
    assert rb.is_full() is True, "A buffer that overwrote items is still full."


def test_container_features_come_free():
    rb = make(3, 1, 2, 3, 4)
    assert 2 in rb and 4 in rb, "`in` works through __iter__ once it is defined; check that __iter__ yields the current items."
    assert 1 not in rb, "1 was overwritten, so it must not be found."
    assert sum(rb) == 9 and max(rb) == 4 and sorted(rb, reverse=True) == [4, 3, 2], "Built-ins use __iter__."
    assert bool(RingBuffer(3)) is False and bool(rb) is True, "An empty buffer is falsy because __len__ is 0 (no __bool__ needed)."


def test_iterators_are_independent():
    rb = make(3, 1, 2, 3)
    first, second = iter(rb), iter(rb)
    assert next(first) == 1 and next(first) == 2, "iter() must work."
    assert next(second) == 1, "Each iter(rb) starts again from the beginning: make __iter__ a generator."


def test_repr():
    assert repr(make(3, 1, 2)) == "RingBuffer([1, 2], capacity=3)", "repr should be RingBuffer([1, 2], capacity=3): list in order, then capacity."
    assert repr(make(2, "a", "b", "c")) == "RingBuffer(['b', 'c'], capacity=2)", "Use !r for the items so strings show quotes; show oldest first."
