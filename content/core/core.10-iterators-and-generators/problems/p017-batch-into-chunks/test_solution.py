from itertools import islice

import pytest

from solution import batches

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
    assert list(batches([1, 2, 3, 4, 5, 6, 7], 3)) == [[1, 2, 3], [4, 5, 6], [7]], "Groups of 3 in order; the last group is shorter."


def test_exact_multiple():
    assert list(batches(range(4), 2)) == [[0, 1], [2, 3]], "When the length is a multiple of n, do not yield an empty list at the end."


def test_empty():
    assert list(batches([], 5)) == [], "An empty input gives no batches at all, not [[]]."


def test_each_batch_is_a_new_list():
    result = list(batches("abcd", 2))
    assert result == [["a", "b"], ["c", "d"]], "Each batch must keep its own items. Did you clear and reuse one list?"


def test_is_generator():
    result = batches([1, 2, 3], 2)
    assert iter(result) is result, "batches must be a generator function (use yield), not return a list."


def test_endless_input():
    assert list(islice(batches(endless(), 2), 3)) == [[0, 1], [2, 3], [4, 5]], "Must work on an endless stream: never call list() on the input."


def test_reads_only_one_batch():
    log = []
    first = next(batches(counted(range(100), log), 3))
    assert first == [0, 1, 2], "The first batch is the first 3 items."
    assert len(log) <= 3, "To give the first batch, read at most n items from the source."


def test_bad_n():
    with pytest.raises(ValueError):
        list(batches([1, 2, 3], 0))
