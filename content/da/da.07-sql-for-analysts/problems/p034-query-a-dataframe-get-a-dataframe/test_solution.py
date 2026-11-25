import pandas as pd
from solution import revenue_by_plan

orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005, 9006],
    "user_id": [1, 2, 3, 1, 2, 4],
    "order_time": pd.to_datetime(["2025-05-01", "2025-05-03", "2025-05-04", "2025-06-01", "2025-06-02", "2025-06-03"]),
    "plan": ["monthly", "annual", "monthly", "monthly", "annual", "quarterly"],
    "amount": [499, 3999, 499, 499, 3999, 1299]})


def rows(df):
    return [(r.plan, int(r.orders), float(r.revenue)) for r in df.itertuples()]


def test_result_is_a_dataframe(con):
    df = revenue_by_plan(con, orders)
    assert isinstance(df, pd.DataFrame), "Return a pandas DataFrame: end the query with .df()."
    assert list(df.columns) == ["plan", "orders", "revenue"], "Columns: plan, orders, revenue."


def test_values_and_order(con):
    df = revenue_by_plan(con, orders)
    assert rows(df) == [("annual", 2, 7998.0), ("monthly", 3, 1497.0), ("quarterly", 1, 1299.0)], \
        "Group by plan and sort by revenue from largest to smallest."


def test_ties_are_sorted_by_plan(con):
    o = pd.DataFrame({"order_id": [1, 2, 3], "user_id": [1, 2, 3], "order_time": pd.to_datetime(["2025-06-01"] * 3),
                      "plan": ["b", "a", "c"], "amount": [100, 100, 50]})
    assert [r[0] for r in rows(revenue_by_plan(con, o))] == ["a", "b", "c"], "Equal revenue: sort by plan (A to Z) as the tie-break."


def test_connection_is_still_usable(con):
    revenue_by_plan(con, orders)
    assert con.execute("SELECT 42").fetchall() == [(42,)], "The connection must be free for the next query: do not leave a result open (no fetchone)."


def test_second_call_sees_new_data(con):
    revenue_by_plan(con, orders)
    o2 = pd.DataFrame({"order_id": [1], "user_id": [1], "order_time": pd.to_datetime(["2025-06-01"]), "plan": ["annual"], "amount": [10]})
    assert rows(revenue_by_plan(con, o2)) == [("annual", 1, 10.0)], "Register the DataFrame on every call (registering again replaces the old one)."
