import pytest

from target import triangle_kind

CASES = [
    (3, 3, 3, "equilateral"),
    (3, 3, 4, "isosceles"),
    (3, 4, 3, "isosceles"),
    (4, 3, 3, "isosceles"),
    (3, 4, 5, "scalene"),
    (1, 2, 3, "invalid"),
    (0, 1, 1, "invalid"),
    (-1, 2, 2, "invalid"),
    (2, 2, 5, "invalid"),
    (5, 2, 2, "invalid"),
    (2, 5, 2, "invalid"),
    (2, 2, 3, "isosceles"),
]
IDS = ["equilateral", "isosceles-first-two", "isosceles-first-last", "isosceles-last-two", "scalene",
       "flat-line", "zero-side", "negative-side", "isosceles-but-too-short", "long-first-side",
       "long-middle-side", "isosceles-barely-valid"]


@pytest.mark.parametrize("a, b, c, expected", CASES, ids=IDS)
def test_kind(a, b, c, expected):
    assert triangle_kind(a, b, c) == expected, f"({a}, {b}, {c}) should be {expected}"
