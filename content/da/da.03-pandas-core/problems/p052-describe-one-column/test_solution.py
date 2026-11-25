import math
import statistics

import numpy as np
import pandas as pd
import pytest

from solution import describe_column

KEYS = ["n", "missing", "mean", "median", "sd", "q1", "q3", "skew"]


def da01(values):
    """The numbers of da.01, from the statistics module and the sample-skewness formula."""
    n = len(values)
    out = {"n": n, "mean": statistics.fmean(values), "median": statistics.median(values)}
    out["sd"] = statistics.stdev(values) if n >= 2 else None
    if n >= 2:
        q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    else:
        q1 = q3 = values[0]
    out["q1"], out["q3"] = q1, q3
    if n >= 3 and out["sd"] > 0:
        m, sd = out["mean"], out["sd"]
        out["skew"] = n / ((n - 1) * (n - 2)) * sum(((v - m) / sd) ** 3 for v in values)
    else:
        out["skew"] = None
    return out


def check(raw, what):
    s = pd.Series(raw, dtype="float64")
    before = s.copy()
    got = describe_column(s)
    pd.testing.assert_series_equal(s, before, obj="the input Series")
    assert isinstance(got, dict) and set(got) == set(KEYS), f"{what}: the keys should be {KEYS}, got {sorted(got) if isinstance(got, dict) else type(got).__name__}."
    values = [v for v in raw if v is not None and not (isinstance(v, float) and math.isnan(v))]
    assert got["n"] == len(values) and isinstance(got["n"], int), f"{what}: n counts the non-missing values ({len(values)}), got {got['n']!r}."
    assert got["missing"] == len(raw) - len(values) and isinstance(got["missing"], int), f"{what}: missing should be {len(raw) - len(values)}, got {got['missing']!r}."
    want = da01(values)
    for k in ["mean", "median", "sd", "q1", "q3", "skew"]:
        if want[k] is None:
            assert got[k] is None, f"{what}: {k} does not exist here, so it should be None, got {got[k]!r}."
        else:
            assert isinstance(got[k], float), f"{what}: {k} should be a plain Python float, got {type(got[k]).__name__}."
            assert got[k] == pytest.approx(want[k], rel=1e-9, abs=1e-9), (
                f"{what}: {k} should be {want[k]}, got {got[k]}. "
                + {"sd": "Sample sd divides by n - 1 (pandas std() does that by default).",
                   "skew": "Use Series.skew(): it is the adjusted sample skewness.",
                   "q1": "quantile(0.25) uses linear interpolation, like method='inclusive'."}.get(k, "Missing values must be skipped."))


def test_the_da01_example_with_a_gap():
    check([10, 15, 20, 25, 100, None], "example")


def test_no_gaps_and_odd_length():
    check([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0, 11.0], "no gaps")


def test_many_missing_values_and_nan():
    check([None, 3.0, float("nan"), 8.0, 1.0, None, 4.0, 4.0], "gaps as None and NaN")


def test_tiny_inputs():
    check([7.0], "one value")
    check([7.0, 9.0], "two values")
    check([1.0, 2.0, 4.0], "three values")


def test_no_values_at_all():
    got = describe_column(pd.Series([None, None], dtype="float64"))
    assert got["n"] == 0 and got["missing"] == 2, f"n 0 and missing 2, got {got['n']} and {got['missing']}."
    assert all(got[k] is None for k in ["mean", "median", "sd", "q1", "q3", "skew"]), f"with no values every statistic is None, got {got}."
    empty = describe_column(pd.Series([], dtype="float64"))
    assert empty["n"] == 0 and empty["missing"] == 0, "an empty Series: n 0 and missing 0."


def test_constant_column_has_no_skew_to_report():
    got = describe_column(pd.Series([5.0, 5.0, 5.0, 5.0]))
    assert got["sd"] == 0.0 and got["skew"] is None, f"a constant column: sd 0.0 and skew None (NaN becomes None); got sd {got['sd']!r}, skew {got['skew']!r}."


def test_random_columns_match_da01():
    rng = np.random.default_rng(52)
    for i in range(10):
        n = int(rng.integers(3, 80))
        vals = rng.gamma(2.0, 3.0, n).round(3).tolist()
        for j in rng.choice(n, size=n // 5, replace=False):
            vals[int(j)] = None
        check(vals, f"random column {i}")
