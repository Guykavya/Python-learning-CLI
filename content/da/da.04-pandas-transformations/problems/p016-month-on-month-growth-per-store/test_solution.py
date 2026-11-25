import math

import pandas as pd
import pytest

from solution import store_growth


def monthly():
    rows = [
        ("S2", "2025-03", 40.0), ("S1", "2025-02", 150.0), ("S3", "2025-03", 100.0), ("S1", "2025-05", 60.0),
        ("S2", "2025-01", 0.0), ("S1", "2025-01", 100.0), ("S1", "2025-04", 0.0), ("S3", "2025-02", 80.0),
        ("S1", "2025-03", 120.0), ("S2", "2025-02", 0.0),
    ]
    return pd.DataFrame(rows, columns=["store_id", "month", "revenue"])


def result():
    out = store_growth(monthly())
    assert "growth_pct" in out.columns, "add a column named growth_pct."
    return out


def as_list(s):
    return [None if pd.isna(v) else round(v, 6) for v in s.tolist()]


def test_sorted_and_reindexed():
    out = result()
    assert list(zip(out["store_id"], out["month"]))[:5] == [
        ("S1", "2025-01"), ("S1", "2025-02"), ("S1", "2025-03"), ("S1", "2025-04"), ("S1", "2025-05")], (
        "sort by store_id, then month, before comparing with the previous month.")
    assert out.index.tolist() == list(range(10)), "index 0..n-1 after sorting."


def test_growth_inside_one_store():
    got = as_list(result()["growth_pct"])[:5]
    assert got[1] == 50.0 and got[2] == -20.0 and got[3] == -100.0, (
        "S1: 100 -> 150 is +50%, 150 -> 120 is -20%, 120 -> 0 is -100%. Did you multiply by 100? Got %s." % got)


def test_first_month_is_missing():
    got = as_list(result()["growth_pct"])
    assert got[0] is None and got[5] is None and got[8] is None, (
        "the first month of every store has no previous month: missing. If S2's first month shows a number, the "
        "comparison crossed from S1 into S2 (pct_change without groupby).")
    assert got[9] == 25.0, "S3: 80 -> 100 is +25%."


def test_after_a_zero_month_is_missing_not_inf():
    got = result()["growth_pct"].tolist()
    assert not any(isinstance(v, float) and math.isinf(v) for v in got), (
        "growth after a month of 0 revenue must be missing, not inf: replace inf with NaN after pct_change.")
    assert pd.isna(got[4]), "S1: 0 -> 60 has no meaningful percentage: missing."
    assert pd.isna(got[6]), "S2: 0 -> 0 is 0/0: missing."
    assert pd.isna(got[7]), "S2: 0 -> 40 is x/0: missing, not inf."


def test_input_not_changed():
    df = monthly()
    before = df.copy()
    store_growth(df)
    pd.testing.assert_frame_equal(df, before, obj="the input monthly table")
