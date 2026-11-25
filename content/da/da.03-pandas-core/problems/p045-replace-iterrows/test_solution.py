import time

import numpy as np
import pandas as pd

from solution import line_totals


def line_totals_loop(df):
    totals = []
    for _, row in df.iterrows():
        if row["qty"] >= 10:
            discount = 0.10
        elif row["qty"] >= 5:
            discount = 0.05
        else:
            discount = 0.0
        totals.append(row["qty"] * row["unit_price"] * (1 - discount))
    return pd.Series(totals, index=df.index, name="total")


def make(n, seed):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({"qty": rng.integers(1, 16, n), "unit_price": rng.gamma(4.0, 120.0, n).round(2)})


def test_boundaries_and_index():
    df = pd.DataFrame({"qty": [1, 4, 5, 9, 10, 11, 0], "unit_price": [10.0] * 7}, index=list("abcdefg"))
    before = df.copy()
    got = line_totals(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
    assert isinstance(got, pd.Series), f"return a Series, not a {type(got).__name__}."
    assert got.name == "total", f"the Series must be named 'total', got {got.name!r}."
    assert got.index.tolist() == list("abcdefg"), "keep the index of the input."
    want = [10.0, 40.0, 47.5, 85.5, 90.0, 99.0, 0.0]
    assert np.allclose(got.to_numpy(), want), (
        f"expected {want}, got {got.tolist()}. qty 5 and 9 get 5% off, qty 10 and 11 get 10% off, qty 4 gets none: "
        "the boundaries belong to the higher tier (>=).")


def test_random_frame_equals_the_loop():
    df = make(2000, 45)
    want = line_totals_loop(df)
    got = line_totals(df)
    pd.testing.assert_series_equal(got, want, check_dtype=False, rtol=1e-9, obj="line totals")


def test_odd_index_is_kept():
    df = make(50, 1)
    df.index = np.arange(50)[::-1] + 500
    got = line_totals(df)
    assert got.index.tolist() == df.index.tolist(), "the result must use the same index as the input (not 0..n-1)."
    pd.testing.assert_series_equal(got, line_totals_loop(df), check_dtype=False, rtol=1e-9)


def best_of(fn, repeat=3):
    out = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        out.append(time.perf_counter() - t0)
    return min(out)


def test_no_python_loop_over_rows():
    line_totals(make(100, 0))                    # warm-up
    big = make(200_000, 7)
    sample = big.iloc[:2_000]

    baseline = best_of(lambda: line_totals_loop(sample), repeat=1) * 100   # the iterrows loop, scaled to 200,000 rows
    mine = best_of(lambda: line_totals(big))
    assert mine < baseline / 10, (
        f"line_totals took {mine * 1000:.0f} ms on 200,000 rows; the iterrows loop would take about {baseline * 1000:.0f} ms "
        "on this machine, and yours must be at least 10 times faster. No iterrows, no apply(axis=1), no loop over rows: "
        "use np.select (or where) and column arithmetic.")
