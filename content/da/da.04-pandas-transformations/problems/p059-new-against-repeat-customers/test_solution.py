import random
from datetime import date, timedelta

import pandas as pd
import pytest

from solution import new_vs_repeat

COLUMNS = ["month", "new_customers", "repeat_customers", "new_revenue", "repeat_revenue"]


def slow_new_vs_repeat(orders):
    """Loop over the orders: first month per customer, then sets and sums per month."""
    rows = list(zip(orders["customer_id"], orders["order_date"], orders["revenue"]))
    first = {}
    for c, d, _ in rows:
        m = "%04d-%02d" % (d.year, d.month)
        if c not in first or m < first[c]:
            first[c] = m
    table = {}
    for c, d, r in rows:
        m = "%04d-%02d" % (d.year, d.month)
        t = table.setdefault(m, {"new": set(), "repeat": set(), "new_rev": 0.0, "repeat_rev": 0.0})
        kind = "new" if first[c] == m else "repeat"
        t[kind].add(c)
        t[kind + "_rev"] += r
    return [[m, len(t["new"]), len(t["repeat"]), t["new_rev"], t["repeat_rev"]] for m, t in sorted(table.items())]


def fixed():
    return pd.DataFrame({
        "order_id": [10007, 10001, 10003, 10002, 10005, 10004, 10006, 10008],
        "customer_id": ["C2", "C1", "C1", "C2", "C3", "C3", "C1", "C4"],
        "order_date": pd.to_datetime(["2025-03-01", "2025-01-05", "2025-02-10", "2025-01-15",
                                      "2025-02-25", "2025-02-03", "2025-01-20", "2025-03-15"]),
        "revenue": [20.0, 100.0, 30.0, 200.0, 10.0, 70.0, 50.0, 40.0],
    })


def random_orders(seed):
    rng = random.Random(seed)
    n = rng.randint(3, 60)
    custs = ["C%02d" % i for i in range(1, rng.randint(2, 15) + 1)]
    return pd.DataFrame({
        "order_id": range(10001, 10001 + n),
        "customer_id": [rng.choice(custs) for _ in range(n)],
        "order_date": pd.to_datetime([(date(2024, 11, 1) + timedelta(days=rng.randint(0, 200))).isoformat() for _ in range(n)]),
        "revenue": [round(rng.uniform(40, 900), 2) for _ in range(n)],
    })


def test_columns():
    out = new_vs_repeat(fixed())
    assert list(out.columns) == COLUMNS, "columns %s; got %s" % (COLUMNS, list(out.columns))
    assert out.index.tolist() == list(range(len(out))), "fresh index"


def test_fixed_months():
    out = new_vs_repeat(fixed())
    got = out.values.tolist()
    assert [r[0] for r in got] == ["2025-01", "2025-02", "2025-03"], "one row per month with orders, sorted, as 'YYYY-MM' text"
    assert got[0][1:] == [2, 0, 350.0, 0.0], (
        "January: C1 (two orders, 100 + 50) and C2 (200) are both new: 2 new customers (not 3: count DISTINCT customers), "
        "350 new revenue; got %s" % got[0][1:])
    assert got[1][1:] == [1, 1, 80.0, 30.0], "February: C3 new (70 + 10), C1 repeat (30); got %s" % got[1][1:]
    assert got[2][1:] == [1, 1, 40.0, 20.0], "March: C4 new (40), C2 repeat (20); got %s" % got[2][1:]


def test_no_repeat_customers_at_all():
    o = fixed()[fixed()["order_date"] < "2025-02-01"]
    out = new_vs_repeat(o)
    assert list(out.columns) == COLUMNS, "even with no repeat customer, every column must exist (reindex after unstack)"
    assert out.values.tolist() == [["2025-01", 2, 0, 350.0, 0.0]], "nobody repeats in January alone: repeat counts are 0"


def test_dtypes():
    out = new_vs_repeat(fixed())
    assert str(out["new_customers"].dtype) == "int64" and str(out["repeat_customers"].dtype) == "int64", "customer counts are integers"
    assert str(out["new_revenue"].dtype) == "float64", "revenue sums are floats"


@pytest.mark.parametrize("seed", range(12))
def test_matches_loop(seed):
    o = random_orders(seed)
    got = new_vs_repeat(o).values.tolist()
    want = slow_new_vs_repeat(o)
    assert [r[:3] for r in got] == [r[:3] for r in want], "months or customer counts differ from the loop (seed %d)" % seed
    assert [r[3:] for r in got] == [pytest.approx(r[3:]) for r in want], "revenue differs from the loop (seed %d)" % seed


def test_revenue_reconciles():
    out = new_vs_repeat(fixed())
    assert (out["new_revenue"] + out["repeat_revenue"]).sum() == pytest.approx(fixed()["revenue"].sum()), (
        "every order is new or repeat: the two revenue columns must add up to the total (520)")


def test_input_unchanged():
    o = fixed()
    before = o.copy()
    new_vs_repeat(o)
    pd.testing.assert_frame_equal(o, before, obj="orders")
