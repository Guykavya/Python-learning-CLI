from solution import take


def naturals():
    n = 0
    while True:
        yield n
        n += 1


def test_basic():
    assert take([5, 6, 7, 8], 2) == [5, 6], "Return the first n items as a list."
    assert take("abc", 10) == ["a", "b", "c"], "If there are fewer than n items, return them all."


def test_zero():
    assert take([1, 2], 0) == [], "n = 0 gives an empty list."


def test_infinite_source():
    assert take(naturals(), 5) == [0, 1, 2, 3, 4], "take must work on an infinite generator: do not call list() on the input."


def test_does_not_over_consume():
    it = iter([1, 2, 3, 4])
    assert take(it, 2) == [1, 2], "The first two items."
    assert next(it) == 3, "take took more than n items from the iterator. Pull exactly n, no peeking."


def test_zero_consumes_nothing():
    it = iter([1, 2])
    take(it, 0)
    assert next(it) == 1, "take(it, 0) must not use up an item."
