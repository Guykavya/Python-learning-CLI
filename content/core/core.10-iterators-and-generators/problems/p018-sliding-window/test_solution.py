from itertools import islice

from solution import windows

def endless(start=0):
    # Acts like an infinite stream. It stops the test after 10,000 items,
    # so a solution that is not lazy cannot freeze your computer.
    n = start
    while True:
        if n - start >= 10_000:
            raise RuntimeError("Read 10,000 items from an endless stream: your code is not lazy. Did you call list() on the input?")
        yield n
        n += 1


def counted(items, log):
    for item in items:
        log.append(item)
        yield item


def test_basic():
    assert list(windows([1, 2, 3, 4, 5], 3)) == [(1, 2, 3), (2, 3, 4), (3, 4, 5)], "Each window moves one step right. Yield tuples."


def test_string():
    assert list(windows("abc", 2)) == [("a", "b"), ("b", "c")], "Works on any iterable, also a string."


def test_too_short():
    assert list(windows([1, 2], 3)) == [], "Fewer than k items: no window at all. Do not yield a short window."


def test_exact_length():
    assert list(windows([7, 8, 9], 3)) == [(7, 8, 9)], "Exactly k items give exactly one window."


def test_k_one():
    assert list(windows([4, 5], 1)) == [(4,), (5,)], "k = 1: each item alone, as a one-item tuple."


def test_windows_are_independent():
    result = list(windows([1, 2, 3, 4], 2))
    assert result == [(1, 2), (2, 3), (3, 4)], "Every window must keep its own items. Did you yield the same list and keep changing it?"


def test_is_generator():
    result = windows([1, 2, 3], 2)
    assert iter(result) is result, "windows must be a generator function (use yield), not return a list."


def test_endless_input():
    assert list(islice(windows(endless(), 2), 3)) == [(0, 1), (1, 2), (2, 3)], "Must work on an endless stream: never call list() on the input."


def test_reads_only_k_for_first_window():
    log = []
    assert next(windows(counted(range(50), log), 3)) == (0, 1, 2), "The first window is the first k items."
    assert len(log) == 3, "To give the first window, read exactly k items from the source."
