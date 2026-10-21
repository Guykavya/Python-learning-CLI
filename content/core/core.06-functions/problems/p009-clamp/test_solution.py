import pytest
from solution import clamp


@pytest.mark.parametrize("args, kwargs, expected", [
    ((150,), {}, 100), ((-20,), {}, 0), ((42,), {}, 42), ((0,), {}, 0), ((100,), {}, 100),
])
def test_defaults(args, kwargs, expected):
    assert clamp(*args, **kwargs) == expected, f"With the default range 0..100, clamp{args} should be {expected}."


def test_keyword_high():
    assert clamp(7, high=5) == 5, "high=5 by keyword keeps low at its default 0, so 7 becomes 5."


def test_keyword_low():
    assert clamp(50, low=60) == 60, "low=60 with the default high 100: 50 is below, so 60."


def test_floats():
    assert clamp(0.25, low=0.5, high=1.0) == 0.5
    assert clamp(0.75, low=0.5, high=1.0) == 0.75


def test_reversed_range_swapped():
    assert clamp(5, 10, 1) == 5, "low > high: swap them first, then 5 is inside 1..10."
    assert clamp(20, 10, 1) == 10, "After swapping the range is 1..10, so 20 becomes 10."
    assert clamp(-3, high=-10, low=0) == -3, "Range -10..0 after the swap; -3 is inside."


def test_negative_range():
    assert clamp(-50, -10, -1) == -10
