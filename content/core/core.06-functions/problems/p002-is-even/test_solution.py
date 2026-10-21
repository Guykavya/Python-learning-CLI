import pytest
from solution import is_even


@pytest.mark.parametrize("n, expected", [(4, True), (7, False), (0, True), (-3, False), (-8, True), (10**12 + 1, False)])
def test_values(n, expected):
    assert is_even(n) is expected, (
        f"is_even({n}) should return {expected}. Return the comparison n % 2 == 0 itself, "
        "not a string, and do not just print it.")


def test_returns_real_bool():
    assert type(is_even(2)) is bool, "Return True or False (a bool), not 1/0 or a string."


def test_does_not_print(capsys):
    is_even(5)
    assert capsys.readouterr().out == "", "Do not print inside the function; return the bool."
