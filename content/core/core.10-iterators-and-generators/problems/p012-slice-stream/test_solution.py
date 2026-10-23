from itertools import count
from solution import slice_stream


def noisy(log):
    n = 0
    while True:
        log.append(n)
        yield n
        n += 1


def test_basic():
    assert slice_stream(range(100), 3, 6) == [3, 4, 5], "Positions 3, 4, 5."
    assert slice_stream("abcdef", 0, 2) == ["a", "b"], "Works on strings too."


def test_short_input():
    assert slice_stream([1, 2], 5, 9) == [], "Start beyond the end gives an empty list."


def test_infinite_input():
    assert slice_stream(count(10), 2, 5) == [12, 13, 14], "Must work on an infinite iterator: do not call list() on the input."


def test_reads_no_more_than_needed():
    log = []
    assert slice_stream(noisy(log), 1, 4) == [1, 2, 3], "Positions 1, 2, 3."
    assert len(log) <= 4, "Do not pull items beyond position stop - 1 from the source."
