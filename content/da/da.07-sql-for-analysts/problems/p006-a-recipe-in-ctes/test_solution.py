import pandas as pd
import pytest
from solution import QUERY

import re

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_at": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-01-25", "2025-02-14", "2025-03-05"]),
    "channel": ["organic", "ads", "organic", "ads", "referral"],
    "country": ["IN", "IN", "US", "UK", "US"]})
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005],
    "user_id": [1, 1, 2, 3, 4],
    "order_time": pd.to_datetime(["2025-01-10 09:00", "2025-02-12 10:00", "2025-01-20 18:30", "2025-02-03 07:45", "2025-02-25 12:00"]),
    "plan": ["monthly", "monthly", "annual", "monthly", "annual"],
    "amount": [499, 499, 3999, 499, 3999]})


def truth(users, orders):
    first = orders.groupby("user_id")["order_time"].min().rename("first").reset_index()
    tot = orders.groupby("user_id")["amount"].sum().rename("total").reset_index()
    m = first.merge(users[["user_id", "channel"]], on="user_id").merge(tot, on="user_id")
    m["month"] = m["first"].dt.to_period("M").dt.start_time.dt.strftime("%Y-%m-%d")
    g = m.groupby(["channel", "month"]).agg(buyers=("user_id", "size"), revenue=("total", "sum")).reset_index()
    return [tuple(r) for r in g.itertuples(index=False)]


def test_columns(run):
    cols, _ = run(QUERY, users=users, orders=orders)
    assert cols == ["channel", "first_purchase_month", "buyers", "revenue"], "Columns: channel, first_purchase_month, buyers, revenue."


def test_has_three_ctes():
    n = len(re.findall(r"\bAS\s*\(", QUERY, flags=re.I))
    assert n >= 3, f"The recipe needs at least three CTEs (name AS (...)); your query has {n}."


def test_example(run, same):
    _, rows = run(QUERY, users=users, orders=orders)
    want = [("organic", "2025-01-01", 1, 998), ("ads", "2025-01-01", 1, 3999), ("organic", "2025-02-01", 1, 499),
            ("ads", "2025-02-01", 1, 3999)]
    assert same(rows, want), ("Group by the month of the FIRST order, but sum ALL orders of the buyers: "
                              "user 1's February renewal belongs to the January group.")


@pytest.mark.parametrize("seed", [11, 12, 13])
def test_random_data(run, same, data, seed):
    u, _e, o = data(seed, 60)
    _, rows = run(QUERY, users=u, orders=o)
    assert same(rows, truth(u, o)), "Count each buyer once (one row per user at every step) and sum every order."
