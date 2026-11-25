import math

import numpy as np
import pandas as pd

from solution import daily_changes

NAN = float("nan")


def slow(values):
    diff, pct, run = [], [], []
    total = 0.0
    for i, v in enumerate(values):
        total += v
        run.append(total)
        if i == 0:
            diff.append(NAN)
            pct.append(NAN)
        else:
            prev = values[i - 1]
            diff.append(v - prev)
            pct.append((v - prev) / prev if prev != 0 else NAN)
    return diff, pct, run


def same(got, want, what):
    assert len(got) == len(want), f"{what}: expected {len(want)} values, got {len(got)}."
    for i, (g, w) in enumerate(zip(got, want)):
        if math.isnan(w):
            assert isinstance(g, float) and math.isnan(g), f"{what}, row {i}: expected a missing value, got {g!r}."
        else:
            assert not math.isnan(g) and not math.isinf(g) and abs(g - w) < 1e-9, f"{what}, row {i}: expected {w}, got {g!r}."


def test_the_example():
    idx = pd.date_range("2025-03-01", periods=6)
    s = pd.Series([100.0, 120.0, 90.0, 0.0, 50.0, 50.0], index=idx)
    before = s.copy()
    out = daily_changes(s)
    pd.testing.assert_series_equal(s, before, obj="the input Series")
    assert isinstance(out, pd.DataFrame), f"return a DataFrame, not a {type(out).__name__}."
    assert out.columns.tolist() == ["diff", "pct_change", "running_total"], f"columns should be ['diff', 'pct_change', 'running_total'], got {out.columns.tolist()}."
    assert out.index.equals(idx), "keep the index (the dates) of the input."
    same(out["diff"].tolist(), [NAN, 20.0, -30.0, -90.0, 50.0, 0.0], "diff")
    same(out["pct_change"].tolist(), [NAN, 0.2, -0.25, -1.0, NAN, 0.0], "pct_change (after the zero day the change is infinite: it must be missing)")
    same(out["running_total"].tolist(), [100.0, 220.0, 310.0, 310.0, 360.0, 410.0], "running_total")


def test_no_infinite_values_anywhere():
    out = daily_changes(pd.Series([0.0, 5.0, 0.0, 0.0, 3.0]))
    assert not np.isinf(out.to_numpy(dtype=float)).any(), "the result must not contain inf: replace infinite percentages by missing values."
    same(out["pct_change"].tolist(), [NAN, NAN, -1.0, NAN, NAN], "pct_change with zeros (0/0 and x/0 are both missing)")


def test_integer_input_gives_float_percentages():
    out = daily_changes(pd.Series([10, 15, 12]))
    same(out["pct_change"].tolist(), [NAN, 0.5, -0.2], "pct_change of integers")
    assert out["running_total"].tolist() == [10, 25, 37], f"running total of integers: [10, 25, 37], got {out['running_total'].tolist()}."


def test_single_row_and_random_series():
    out = daily_changes(pd.Series([7.0]))
    same(out["diff"].tolist(), [NAN], "single row diff")
    assert out["running_total"].tolist() == [7.0], "a single day: running total is the value itself."
    rng = np.random.default_rng(51)
    vals = rng.integers(0, 5, 60).astype(float).tolist()
    out = daily_changes(pd.Series(vals))
    d, p, r = slow(vals)
    same(out["diff"].tolist(), d, "random diff")
    same(out["pct_change"].tolist(), p, "random pct_change")
    same(out["running_total"].tolist(), r, "random running_total")
