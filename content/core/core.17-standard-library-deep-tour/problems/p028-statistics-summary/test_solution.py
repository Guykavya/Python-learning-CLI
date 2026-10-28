import math

import pytest

from solution import outliers, quartiles, summary

KEYS = {"count", "mean", "median", "modes", "stdev", "pstdev", "range"}


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def test_summary_keys():
    s = summary([2, 4, 4, 4, 5, 5, 7, 9])
    assert set(s) == KEYS, f"Return a dict with exactly these keys: {sorted(KEYS)}."


def test_summary_classic_example():
    s = summary([2, 4, 4, 4, 5, 5, 7, 9])
    assert s["count"] == 8, "count is len(data)."
    assert close(s["mean"], 5.0), "The mean is 40 / 8 = 5.0."
    assert close(s["median"], 4.5), "With an even count the median is the average of the two middle values: (4 + 5) / 2."
    assert s["modes"] == [4], "multimode returns a LIST of the most common values: [4]."
    assert close(s["pstdev"], 2.0), "pstdev (population) divides by n: here exactly 2.0."
    assert close(s["stdev"], 2.138089935299395), (
        "stdev (sample) divides by n - 1, so it is bigger than pstdev: 2.138... Do not mix them up."
    )
    assert s["range"] == 7, "range is max - min: 9 - 2."


def test_summary_median_does_not_need_sorted_input():
    s = summary([3, 1, 2])
    assert s["median"] == 2, "median sorts for you: the middle of [1, 2, 3] is 2, not data[len // 2] of the unsorted list."
    assert s["modes"] == [3, 1, 2], "When every value appears once, all are modes, in first-seen order (multimode)."
    assert close(s["stdev"], 1.0), "Sample stdev of 1, 2, 3 is 1.0."


def test_summary_several_modes():
    s = summary([1, 1, 2, 2, 3])
    assert s["modes"] == [1, 2], (
        "1 and 2 both appear twice. statistics.mode() would return only one of them; multimode() returns both."
    )


def test_summary_one_value():
    s = summary([5])
    assert s["stdev"] is None, (
        "The sample stdev needs at least two values (statistics.stdev raises StatisticsError). Use None for one value."
    )
    assert s["pstdev"] == 0.0 and s["range"] == 0 and close(s["mean"], 5.0), "One value: no spread, mean = the value."


def test_summary_empty():
    with pytest.raises(ValueError):
        summary([])
    # statistics.StatisticsError is a subclass of ValueError, but raise it yourself before any other work


def test_summary_floats():
    s = summary([0.1, 0.2, 0.3])
    assert close(s["mean"], 0.2), "Use isclose-style thinking: the float mean of 0.1, 0.2, 0.3 is 0.2 (up to rounding)."


def test_quartiles():
    assert quartiles([1, 2, 3, 4, 5, 6, 7, 8]) == [2.25, 4.5, 6.75], (
        "Use statistics.quantiles(data, n=4) with its DEFAULT method ('exclusive'): [2.25, 4.5, 6.75]."
    )
    assert quartiles([9, 4, 5, 2, 4, 7, 5, 4]) == [4.0, 4.5, 6.5], "quantiles sorts the data itself."


def test_outliers():
    data = [10, 12, 11, 13, 12, 11, 95, 12, -40]
    assert outliers(data) == [95, -40], (
        "Q1 = 10.5, Q3 = 12.5, IQR = 2, so the fences are 7.5 and 15.5. Keep values outside them, "
        "in their ORIGINAL order."
    )
    assert outliers([1, 2, 3, 4, 5, 6, 7, 8]) == [], "Evenly spread data has no outliers."


def test_inputs_not_changed():
    data = [3, 1, 2]
    summary(data)
    quartiles(data)
    outliers(data)
    assert data == [3, 1, 2], "Do not sort the caller's list in place."
