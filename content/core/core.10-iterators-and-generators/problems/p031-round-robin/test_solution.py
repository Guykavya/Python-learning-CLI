from itertools import islice

from solution import round_robin

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
    assert list(round_robin("abc", "d", "ef")) == ["a", "d", "e", "b", "f", "c"], "One item from each in turn; skip the ones that are finished."


def test_empty_one_in_the_middle():
    assert list(round_robin([1, 2], [], [3])) == [1, 3, 2], "An empty iterable is simply skipped."


def test_no_iterables():
    assert list(round_robin()) == [], "No iterables give nothing."


def test_single():
    assert list(round_robin([7, 8, 9])) == [7, 8, 9], "One iterable gives its own items in order."


def test_lists_do_not_restart():
    assert list(round_robin([1, 2], [3, 4])) == [1, 3, 2, 4], "Call iter() once per input, not in every round, or a list restarts."


def test_is_generator():
    result = round_robin([1], [2])
    assert iter(result) is result, "round_robin must be a generator function (use yield)."


def test_endless_source():
    assert list(islice(round_robin([1, 2], endless(100)), 6)) == [1, 100, 2, 101, 102, 103], "Must work with an endless source: never call list() on an input."


def test_reads_only_when_needed():
    log_a, log_b = [], []
    rr = round_robin(counted("xyz", log_a), counted("pq", log_b))
    assert next(rr) == "x", "The first item comes from the first iterable."
    assert len(log_a) == 1, "Read only one item from a source per turn."
    assert next(rr) == "p", "The second item comes from the second iterable."
    assert len(log_a) == 1 and len(log_b) == 1, "After two items, each source has given exactly one."
