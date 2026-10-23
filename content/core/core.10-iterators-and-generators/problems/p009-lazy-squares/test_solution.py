import types
from solution import lazy_squares


def noisy(log):
    for n in (1, 2, 3):
        log.append(n)
        yield n


def test_values():
    assert list(lazy_squares([1, 2, 3])) == [1, 4, 9], "Each item must be squared."
    assert sum(lazy_squares(range(4))) == 14, "0 + 1 + 4 + 9."


def test_is_generator():
    assert isinstance(lazy_squares([1]), types.GeneratorType), "Return a generator expression, not a list: use round brackets."


def test_nothing_pulled_until_asked():
    log = []
    g = lazy_squares(noisy(log))
    assert log == [], "Creating the generator must not pull anything from the source yet."
    assert next(g) == 1, "First value is 1 squared."
    assert log == [1], "Only one item should have been pulled after one next()."
    assert next(g) == 4, "Second value is 2 squared."
    assert log == [1, 2], "Items are pulled on demand, one per next()."


def test_consumed_once():
    g = lazy_squares([1, 2])
    assert list(g) == [1, 4], "First pass gives the values."
    assert list(g) == [], "A generator can be used once: the second pass is empty."
