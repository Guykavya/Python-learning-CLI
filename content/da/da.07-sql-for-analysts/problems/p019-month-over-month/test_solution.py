import pandas as pd
import pytest
from solution import QUERY

orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005],
    "user_id": [1, 2, 3, 1, 4],
    "order_time": pd.to_datetime(["2025-01-05 10:00", "2025-01-20 11:00", "2025-02-14 09:00", "2025-04-02 18:00", "2025-04-30 23:30"]),
    "plan": ["monthly", "annual", "monthly", "monthly", "annual"],
    "amount": [400, 600, 1500, 200, 400]})


def truth(orders):
    m = orders["order_time"].dt.to_period("M")
    s = orders.groupby(m)["amount"].sum()
    s = s.reindex(pd.period_range(m.min(), m.max(), freq="M"), fill_value=0)
    out, prev = [], None
    for p, v in s.items():
        v = int(v)
        if prev is None:
            out.append((p.start_time.strftime("%Y-%m-%d"), v, None, None, None))
        else:
            out.append((p.start_time.strftime("%Y-%m-%d"), v, prev, v - prev, (v - prev) * 100.0 / prev if prev else None))
        prev = v
    return out


def test_columns(run):
    cols, _ = run(QUERY, orders=orders)
    assert cols == ["month", "revenue", "prev_revenue", "change", "pct_change"], "Columns: month, revenue, prev_revenue, change, pct_change."


def test_example(run, same):
    _, rows = run(QUERY, orders=orders)
    want = [("2025-01-01", 1000, None, None, None), ("2025-02-01", 1500, 1000, 500, 50.0),
            ("2025-03-01", 0, 1500, -1500, -100.0), ("2025-04-01", 600, 0, 600, None)]
    assert len(rows) == 4, "March has no orders but still needs a row (revenue 0): build the months with generate_series first."
    assert same(rows, want), "April's previous month is March (0), so its pct_change is NULL; the first month has NULL in every comparison column."


def test_no_infinity(run):
    _, rows = run(QUERY, orders=orders)
    assert all(r[4] is None or r[4] != float("inf") for r in rows), "A percentage change from 0 must be NULL (divide by NULLIF(prev, 0)), not inf."


@pytest.mark.parametrize("seed", [32, 33])
def test_random_data(run, same, data, seed):
    _u, _e, o = data(seed, 40)
    _, rows = run(QUERY, orders=o)
    assert same(rows, truth(o)), "Complete the months, then lag over the months."
