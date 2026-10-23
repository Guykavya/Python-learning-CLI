import inspect
import types
import pytest
from solution import countdown


def test_is_generator_function():
    assert inspect.isgeneratorfunction(countdown), "countdown must contain 'yield'. A function that returns a list is not a generator function."


def test_values():
    assert list(countdown(3)) == [3, 2, 1], "countdown(3) must give 3, 2, 1 (stop before 0)."
    assert list(countdown(1)) == [1], "countdown(1) gives just 1."


def test_zero_and_negative():
    assert list(countdown(0)) == [], "countdown(0) yields nothing."
    assert list(countdown(-4)) == [], "A negative start yields nothing."


def test_returns_generator_and_exhausts():
    g = countdown(2)
    assert isinstance(g, types.GeneratorType), "Calling countdown must return a generator object."
    assert next(g) == 2, "The first next() gives n."
    assert next(g) == 1, "The second next() gives n - 1."
    with pytest.raises(StopIteration):
        next(g)


def test_big_n_is_lazy():
    g = countdown(10**12)
    assert next(g) == 10**12, "Do not build all the numbers first: countdown(10**12) must answer instantly."
