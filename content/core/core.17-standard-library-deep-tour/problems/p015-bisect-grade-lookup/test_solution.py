import inspect
import random

import solution
from solution import count_in_range, grade


def test_grade_middles():
    assert [grade(s) for s in (0, 65, 75, 85, 95)] == ["F", "D", "C", "B", "A"], "One score inside each band."


def test_grade_boundaries():
    assert grade(59) == "F", "59 is below 60: F."
    assert grade(60) == "D", "A score EQUAL to a breakpoint gets the higher grade. bisect_left(…, 60) gives 0 (F); use bisect_right."
    assert grade(90) == "A", "90 is exactly the A breakpoint: A."
    assert grade(89) == "B", "89 is still B."
    assert grade(100) == "A", "Above the top breakpoint: the last grade."


def test_grade_custom():
    assert grade(5, [3, 6], "xyz") == "y", "With breakpoints [3, 6], 5 is in the middle band."
    assert grade(6, [3, 6], "xyz") == "z", "Equal to the last breakpoint: the last grade."
    assert grade(-1, [3, 6], "xyz") == "x", "Below everything: the first grade."
    assert grade(50, [50], "NY") == "Y", "One breakpoint, two grades."


def test_count_basic():
    a = [1, 3, 3, 3, 5, 8]
    assert count_in_range(a, 3, 5) == 4, "Both ends included, duplicates counted: 3, 3, 3, 5."
    assert count_in_range(a, 4, 4) == 0, "Nothing equals 4."
    assert count_in_range(a, 3, 3) == 3, "lo == hi counts the copies of that value: bisect_right(a, 3) - bisect_left(a, 3)."
    assert count_in_range(a, 0, 100) == 6, "A range covering everything."
    assert count_in_range(a, 9, 20) == 0, "A range above everything."


def test_count_edges():
    assert count_in_range([], 1, 2) == 0, "Empty list: 0."
    assert count_in_range([1, 2, 3], 3, 1) == 0, "lo > hi is an empty range: 0, never a negative number."
    assert count_in_range([2, 4], 2, 4) == 2, "Both endpoints are values in the list: count them both."


def test_count_matches_brute_force():
    rng = random.Random(15)
    a = sorted(rng.randint(0, 30) for _ in range(200))
    for _ in range(200):
        lo = rng.randint(-5, 35)
        hi = rng.randint(-5, 35)
        expected = sum(1 for n in a if lo <= n <= hi)
        assert count_in_range(a, lo, hi) == expected, f"count_in_range(a, {lo}, {hi}) should be {expected}."


def test_uses_bisect():
    src = inspect.getsource(solution.count_in_range)
    assert "bisect" in src, "Use bisect_left / bisect_right: two O(log n) searches instead of a loop over the list."
