import pytest

from solution import repeat


def test_returns_list_of_results():
    @repeat(3)
    def roll(sides=6):
        """Pretend dice roll."""
        return sides

    assert roll() == [6, 6, 6], "Call the function n times and return a list of the n results."
    assert roll(sides=20) == [20, 20, 20], "Keyword arguments must pass through to every call."


def test_calls_n_times_in_order():
    seen = []

    @repeat(4)
    def step(x):
        seen.append(x)
        return len(seen)

    assert step("a") == [1, 2, 3, 4], "The results must be in call order: one list item per call."
    assert seen == ["a", "a", "a", "a"], "Each of the n calls must get the same arguments."


def test_n_one():
    @repeat(1)
    def one():
        return "x"

    assert one() == ["x"], "repeat(1) still returns a list, with one item."


def test_metadata():
    @repeat(2)
    def roll():
        """Pretend dice roll."""
        return 1

    assert roll.__name__ == "roll", "Use @functools.wraps(func) on the innermost wrapper."
    assert roll.__doc__ == "Pretend dice roll.", "wraps also keeps the docstring."


def test_bad_n_fails_early():
    with pytest.raises(ValueError):
        repeat(0)
    with pytest.raises(ValueError):
        repeat(-2)


def test_no_call_at_decoration():
    seen = []

    @repeat(3)
    def f():
        seen.append(1)

    assert seen == [], "Decorating must not call the function. Only calls of the wrapper do."
