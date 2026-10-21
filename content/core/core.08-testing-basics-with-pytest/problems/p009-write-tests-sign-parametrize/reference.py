import pytest

from target import sign


@pytest.mark.parametrize("n, expected", [
    (5, 1), (1, 1), (1000000, 1),
    (0, 0),
    (-1, -1), (-5, -1), (-1000000, -1),
    (0.5, 1), (-0.5, -1),
])
def test_sign_table(n, expected):
    assert sign(n) == expected, f"sign({n}) should be {expected}, not {sign(n)}."


def test_zero_is_neither_positive_nor_negative():
    assert sign(0) == 0, "Zero has sign 0."
