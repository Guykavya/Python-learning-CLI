import math

import numpy as np
import pytest

from solution import grades


def slow(v):
    if math.isnan(v):
        return "missing"
    for cut, g in [(90, "A"), (75, "B"), (60, "C"), (40, "D")]:
        if v >= cut:
            return g
    return "F"


def test_example():
    got = grades(np.array([92, 89.5, 75, 60, 39.9, np.nan]))
    assert got.tolist() == ["A", "B", "B", "C", "F", "missing"], f"got {got.tolist()}."


def test_boundaries_belong_to_the_higher_grade():
    got = grades(np.array([90.0, 75.0, 60.0, 40.0]))
    assert got.tolist() == ["A", "B", "C", "D"], (
        f"got {got.tolist()}: each boundary belongs to the higher grade, use >=. "
        "If 90 became B, check the order: np.select takes the FIRST true condition, so list the strictest first.")


def test_just_below_each_boundary():
    got = grades(np.array([89.99, 74.99, 59.99, 39.99, 0.0]))
    assert got.tolist() == ["B", "C", "D", "F", "F"], f"got {got.tolist()}."


def test_order_of_conditions():
    got = grades(np.array([100.0]))
    assert got.tolist() == ["A"], (
        "100 is >= 40 as well as >= 90: if you got D, your conditions are in the wrong order; np.select takes the first true one.")


def test_nan_is_missing_not_f():
    got = grades(np.array([np.nan, 50.0, np.nan]))
    assert got.tolist() == ["missing", "D", "missing"], (
        "nan compares False with everything, so it falls through to the default 'F'. Test np.isnan(scores) first.")


def test_whole_word_missing_is_kept():
    got = grades(np.array([np.nan]))
    assert got[0] == "missing", f"got {got[0]!r}: the string array was too narrow and cut 'missing' short (Ch. 4.7)."


def test_same_shape_and_string_dtype():
    s = np.array([[95.0, 10.0, 61.0], [np.nan, 75.0, 40.0]])
    got = grades(s)
    assert got.shape == (2, 3), f"the result must have the shape of scores (2, 3), got {got.shape}."
    assert got.dtype.kind == "U", f"the result must be an array of strings, got dtype {got.dtype}."
    assert got.tolist() == [["A", "F", "C"], ["missing", "B", "D"]], f"got {got.tolist()}."


def test_integer_scores():
    got = grades(np.array([90, 74, 0]))
    assert got.tolist() == ["A", "C", "F"], "integer scores work too (they can never be nan)."


@pytest.mark.parametrize("seed", range(5))
def test_random(seed):
    rng = np.random.default_rng(seed)
    s = np.round(rng.uniform(0, 100, size=200), 1)
    s[rng.integers(0, 200, size=15)] = np.nan
    s[:4] = [90, 75, 60, 40]
    got = grades(s)
    assert got.tolist() == [slow(v) for v in s.tolist()], "some grades differ from the table in problem.md."
