from itertools import islice

from solution import unique

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


def test_numbers():
    assert list(unique([3, 1, 3, 2, 1])) == [3, 1, 2], "Keep the FIRST time each item appears, in the original order. A set loses the order."


def test_string():
    assert "".join(unique("banana")) == "ban", "Works on any iterable, also a string."


def test_empty():
    assert list(unique([])) == [], "No items, no output."


def test_key_keeps_original_item():
    emails = ["Ann@x.in", "ann@x.in", "Bob@y.in", "ANN@X.IN", "bob@y.in"]
    assert list(unique(emails, key=str.lower)) == ["Ann@x.in", "Bob@y.in"], "Compare with key(item), but yield the ORIGINAL item, not the lower-case one."


def test_key_with_tuples():
    orders = [("ann", 1), ("bob", 2), ("ann", 3)]
    assert list(unique(orders, key=lambda order: order[0])) == [("ann", 1), ("bob", 2)], "With a key, two items are the same when their keys are equal."


def test_is_generator():
    result = unique([1, 1, 2])
    assert iter(result) is result, "unique must be a generator function (use yield)."


def test_endless_input():
    repeating = (n % 4 for n in endless())
    assert list(islice(unique(repeating), 4)) == [0, 1, 2, 3], "Must work on an endless stream: yield each new item at once, never read the whole input."


def test_yields_new_item_at_once():
    log = []
    assert next(unique(counted([5, 5, 6], log))) == 5, "The first item is always new."
    assert len(log) == 1, "Yield a new item as soon as you see it. Do not read ahead."
