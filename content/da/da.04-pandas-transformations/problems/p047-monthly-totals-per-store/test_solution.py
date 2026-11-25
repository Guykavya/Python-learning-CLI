import calendar
import random
from datetime import date, timedelta

import pandas as pd
import pytest

from solution import store_month


def slow_store_month(orders):
    """Loop version: {(store, 'YYYY-MM-last'): total}."""
    totals = {}
    for store, d, rev in zip(orders["store_id"], orders["order_date"], orders["revenue"]):
        last = calendar.monthrange(d.year, d.month)[1]
        key = (store, "%04d-%02d-%02d" % (d.year, d.month, last))
        totals[key] = totals.get(key, 0.0) + rev
    return sorted(totals.items())


def random_orders(seed):
    rng = random.Random(seed)
    n = rng.randint(5, 60)
    start = date(2024, 1, 1)
    days = [start + timedelta(days=rng.randint(0, 540)) for _ in range(n)]
    return pd.DataFrame({
        "order_id": range(10001, 10001 + n),
        "store_id": [rng.choice(["S1", "S2", "S3", "S4"]) for _ in range(n)],
        "order_date": pd.to_datetime([d.isoformat() for d in days]),
        "revenue": [round(rng.uniform(40, 900), 2) for _ in range(n)],
    })


def fixed():
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 6],
        "store_id": ["S2", "S1", "S1", "S2", "S1", "S2"],
        "order_date": pd.to_datetime(["2025-02-28", "2025-01-05", "2025-03-02", "2025-01-09", "2025-01-31", "2025-02-01"]),
        "revenue": [6.0, 10.0, 20.0, 3.0, 5.0, 4.0],
    })


def as_pairs(out):
    return list(zip(zip(out["store_id"], out["month"].dt.strftime("%Y-%m-%d")), out["revenue"]))


def test_columns():
    out = store_month(fixed())
    assert list(out.columns) == ["store_id", "month", "revenue"], "columns store_id, month, revenue; got %s" % list(out.columns)
    assert out.index.tolist() == list(range(len(out))), "fresh index"


def test_fixed():
    out = store_month(fixed())
    got = as_pairs(out)
    want = [(("S1", "2025-01-31"), 15.0), (("S1", "2025-03-31"), 20.0), (("S2", "2025-01-31"), 3.0), (("S2", "2025-02-28"), 10.0)]
    assert len(got) == 4, "one row per store and month WITH orders: S1 has Jan and Mar, S2 has Jan and Feb (got %d rows)" % len(got)
    assert got == want, "S1 Jan = 10 + 5 (31 Jan is still January), S2 Feb = 4 + 6; labels are month ENDS; got %s" % got


@pytest.mark.parametrize("seed", range(10))
def test_matches_loop(seed):
    o = random_orders(seed)
    got = as_pairs(store_month(o))
    want = slow_store_month(o)
    assert [k for k, _ in got] == [k for k, _ in want], "the (store, month) rows differ from the loop version (seed %d)" % seed
    assert [v for _, v in got] == pytest.approx([v for _, v in want]), "monthly totals differ from the loop version (seed %d)" % seed


def test_input_unchanged():
    o = fixed()
    before = o.copy()
    store_month(o)
    pd.testing.assert_frame_equal(o, before, obj="orders")
