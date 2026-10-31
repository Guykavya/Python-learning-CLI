# Save the code from problem.md as target.py in this folder, then run:
#     python -m pytest solution.py
# The three tests below are copy-pasted. Replace them with ONE parametrized test.
from target import triangle_kind


def test_equilateral():
    assert triangle_kind(3, 3, 3) == "equilateral"


def test_isosceles():
    assert triangle_kind(3, 3, 4) == "isosceles"


def test_scalene():
    assert triangle_kind(3, 4, 5) == "scalene"
