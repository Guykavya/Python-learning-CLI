import pandas as pd
import pytest
from solution import QUERY

users = pd.DataFrame({
    "user_id": [1, 2, 3],
    "signup_at": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-02-02"]),
    "channel": ["organic", "ads", "ads"],
    "country": ["IN", "US", "IN"]})
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005],
    "user_id": [1, 1, 2, 3, 2],
    "order_time": pd.to_datetime(["2025-02-10", "2025-03-10", "2025-02-11", "2025-03-01", "2025-03-20"]),
    "plan": ["monthly", "monthly", "annual", "annual", "monthly"],
    "amount": [499, 499, 3999, 3999, 499]})


def truth(users, orders):
    m = orders.merge(users[["user_id", "country"]], on="user_id")
    g = m.groupby(["plan", "country"], as_index=False)["amount"].sum().rename(columns={"amount": "revenue"})
    g = g.sort_values(["revenue", "plan", "country"], ascending=[False, True, True]).reset_index(drop=True)
    total = g["revenue"].sum()
    g["share"] = g["revenue"] / total
    g["cum"] = g["share"].cumsum()
    return [(r.plan, r.country, int(r.revenue), r.share, r.cum) for r in g.itertuples()]


def test_columns(run):
    cols, _ = run(QUERY, users=users, orders=orders)
    assert cols == ["plan", "country", "revenue", "share", "cumulative_share"], "Columns: plan, country, revenue, share, cumulative_share."


def test_example(run, same):
    _, rows = run(QUERY, users=users, orders=orders)
    t = 9495
    want = [("annual", "IN", 3999, 3999 / t, 3999 / t), ("annual", "US", 3999, 3999 / t, 7998 / t),
            ("monthly", "IN", 998, 998 / t, 8996 / t), ("monthly", "US", 499, 499 / t, 1.0)]
    assert same(rows, want, ordered=True), ("Rows sorted by revenue DESC (ties by plan, then country). The cumulative share of the tied "
                                            "row must NOT equal its neighbour's: use a ROWS frame, not the default RANGE.")


def test_shares_sum_to_one(run):
    _, rows = run(QUERY, users=users, orders=orders)
    assert abs(sum(r[3] for r in rows) - 1) < 1e-9, "The shares must add up to 1: divide by the grand total, sum(revenue) OVER ()."
    assert abs(rows[-1][4] - 1) < 1e-9, "The last cumulative share must be 1."


@pytest.mark.parametrize("seed", [18, 19, 20])
def test_random_data(run, same, data, seed):
    u, _e, o = data(seed, 90)
    _, rows = run(QUERY, users=u, orders=o)
    assert same(rows, truth(u, o), ordered=True), "Aggregate by plan and country, then window over the aggregated rows."
