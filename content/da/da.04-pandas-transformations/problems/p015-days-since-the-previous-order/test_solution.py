import math
import random

import pandas as pd
import pytest

from solution import days_between_orders


def orders():
    return pd.DataFrame({
        "order_id": [15, 11, 12, 16, 13, 14, 17],
        "customer_id": ["B", "A", "A", "C", "A", "B", "A"],
        "order_date": pd.to_datetime(["2025-02-10", "2025-01-01", "2025-01-31", "2025-03-03",
                                      "2025-01-31", "2025-02-01", "2025-03-02"]),
    }, index=[70, 71, 72, 73, 74, 75, 76])


def result():
    out = days_between_orders(orders())
    assert "days_since_prev" in out.columns, "add a column named days_since_prev."
    return out


def test_sorted_and_reindexed():
    out = result()
    assert out["order_id"].tolist() == [11, 12, 13, 17, 14, 15, 16], (
        "sort by customer_id, order_date, order_id. Got %s." % out["order_id"].tolist())
    assert out.index.tolist() == list(range(7)), "index 0..n-1 after sorting."


def test_first_order_of_each_customer_is_missing():
    d = result()["days_since_prev"].tolist()
    for pos, who in [(0, "A"), (4, "B"), (6, "C")]:
        assert math.isnan(d[pos]), (
            "the first order of %s has no previous order: days_since_prev must be missing (NaN), not 0 and not the "
            "gap to another customer's order. Did you diff the whole column without groupby?" % who)


def test_gaps_in_days():
    d = result()["days_since_prev"].tolist()
    assert d[1] == 30.0, "A: Jan 1 -> Jan 31 is 30 days. Got %s." % d[1]
    assert d[2] == 0.0, "A's orders 12 and 13 are on the same day: 0 days, not missing. Got %s." % d[2]
    assert d[3] == 30.0, "A: Jan 31 -> Mar 2 is 30 days (February 2025 has 28 days). Got %s." % d[3]
    assert d[5] == 9.0, "B: Feb 1 -> Feb 10 is 9 days. Got %s." % d[5]


def test_column_is_numeric_days():
    out = result()
    assert pd.api.types.is_float_dtype(out["days_since_prev"]), (
        "days_since_prev must be a float column of days (use .dt.days on the Timedelta), not Timedelta. Got %s."
        % out["days_since_prev"].dtype)


def test_random_against_a_loop():
    rnd = random.Random(21)
    n = 100
    df = pd.DataFrame({
        "order_id": rnd.sample(range(1, 1000), n),
        "customer_id": [rnd.choice("PQRSTU") for _ in range(n)],
        "order_date": pd.to_datetime("2025-01-01") + pd.to_timedelta([rnd.randint(0, 90) for _ in range(n)], unit="D"),
    })
    rows = sorted(zip(df["customer_id"], df["order_date"], df["order_id"]))
    want, prev = [], None
    for c, d, _ in rows:
        want.append((d - prev[1]).days if prev and prev[0] == c else None)
        prev = (c, d)
    got = days_between_orders(df)["days_since_prev"].tolist()
    for g, w in zip(got, want):
        if w is None:
            assert math.isnan(g), "a first order must be NaN."
        else:
            assert g == w, "a gap differs from a plain loop over the sorted orders."


def test_input_not_changed():
    df = orders()
    before = df.copy()
    days_between_orders(df)
    pd.testing.assert_frame_equal(df, before, obj="the input orders")
