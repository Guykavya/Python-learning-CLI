import pandas as pd
import pytest
from solution import QUERY

orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005, 9006],
    "user_id": [1, 1, 2, 1, 2, 3],
    "order_time": pd.to_datetime(["2025-01-10 09:00", "2025-01-12 23:30", "2025-01-15 10:00",
                                  "2025-01-13 00:10", "2025-02-20 08:00", "2025-03-01 12:00"]),
    "plan": ["monthly", "monthly", "annual", "monthly", "monthly", "annual"],
    "amount": [499, 499, 3999, 499, 499, 3999]})


def truth(orders):
    o = orders.sort_values(["user_id", "order_time", "order_id"])
    prev = o.groupby("user_id")["order_time"].shift(1)
    out = []
    for (_, r), p in zip(o.iterrows(), prev):
        if pd.isna(p):
            out.append((int(r["user_id"]), int(r["order_id"]), r["order_time"].strftime("%Y-%m-%d %H:%M:%S"), None, None))
        else:
            days = (r["order_time"].normalize() - p.normalize()).days
            out.append((int(r["user_id"]), int(r["order_id"]), r["order_time"].strftime("%Y-%m-%d %H:%M:%S"), p.strftime("%Y-%m-%d %H:%M:%S"), days))
    return out


def test_columns(run):
    cols, _ = run(QUERY, orders=orders)
    assert cols == ["user_id", "order_id", "order_time", "prev_order_time", "days_since_prev"], "Columns: user_id, order_id, order_time, prev_order_time, days_since_prev."


def test_example(run, same):
    _, rows = run(QUERY, orders=orders)
    want = [(1, 9001, "2025-01-10 09:00:00", None, None), (1, 9002, "2025-01-12 23:30:00", "2025-01-10 09:00:00", 2),
            (1, 9004, "2025-01-13 00:10:00", "2025-01-12 23:30:00", 1), (2, 9003, "2025-01-15 10:00:00", None, None),
            (2, 9005, "2025-02-20 08:00:00", "2025-01-15 10:00:00", 36), (3, 9006, "2025-03-01 12:00:00", None, None)]
    assert same(rows, want), ("The previous order is per user and by TIME (order 9004 comes after 9002). "
                              "Calendar days = difference of the dates: 23:30 to 00:10 the next day is 1.")


def test_first_order_is_null(run):
    _, rows = run(QUERY, orders=orders)
    firsts = [r for r in rows if r[0] == 3]
    assert firsts[0][3] is None and firsts[0][4] is None, "The first order of a user has no previous order: both columns must be NULL (not 0)."


@pytest.mark.parametrize("seed", [14, 15])
def test_random_data(run, same, data, seed):
    _u, _e, o = data(seed, 80)
    _, rows = run(QUERY, orders=o)
    assert same(rows, truth(o)), "lag over PARTITION BY user_id ORDER BY order_time; days = difference of the two DATES."
