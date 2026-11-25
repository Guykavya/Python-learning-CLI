import pandas as pd
import pytest
from solution import QUERY

orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004],
    "user_id": [1, 2, 1, 3],
    "order_time": pd.to_datetime(["2025-06-01 09:00", "2025-06-01 17:30", "2025-06-03 08:15", "2025-06-06 20:00"]),
    "plan": ["monthly", "annual", "monthly", "annual"],
    "amount": [499, 3999, 499, 3999]})


def truth(orders):
    day = orders["order_time"].dt.normalize()
    s = orders.groupby(day)["amount"].sum()
    s = s.reindex(pd.date_range(day.min(), day.max(), freq="D"), fill_value=0).astype(float)
    df = pd.DataFrame({"revenue": s, "running": s.cumsum(), "avg": s.rolling(7, min_periods=1).mean()})
    return [(i.strftime("%Y-%m-%d"), r.revenue, r.running, r.avg) for i, r in df.iterrows()]


def test_columns(run):
    cols, _ = run(QUERY, orders=orders)
    assert cols == ["day", "revenue", "running_total", "avg_7"], "Columns: day, revenue, running_total, avg_7."


def test_example(run, same):
    _, rows = run(QUERY, orders=orders)
    want = [("2025-06-01", 4498, 4498, 4498), ("2025-06-02", 0, 4498, 2249), ("2025-06-03", 499, 4997, 4997 / 3),
            ("2025-06-04", 0, 4997, 4997 / 4), ("2025-06-05", 0, 4997, 4997 / 5), ("2025-06-06", 3999, 8996, 8996 / 6)]
    assert len(rows) == 6, "One row per calendar day from the first to the last order date: 6 days here, including the empty ones."
    assert same(rows, want), "Empty days are 0 (not missing); avg_7 averages the days that exist at the start."


def test_gap_days_count_as_zero(run, same):
    o = pd.DataFrame({"order_id": [1, 2], "user_id": [1, 1], "order_time": pd.to_datetime(["2025-06-01 10:00", "2025-06-10 10:00"]),
                      "plan": ["monthly", "monthly"], "amount": [700, 700]})
    _, rows = run(QUERY, orders=o)
    assert len(rows) == 10, "The calendar has 10 days (1 to 10 June), not 2: use generate_series and a LEFT JOIN."
    assert same([r for r in rows if r[0] == "2025-06-07"], [("2025-06-07", 0, 700, 700 / 7)]), \
        "On 7 June the window holds 7 calendar days (1 to 7 June): one 700 day and six empty days = 100."


@pytest.mark.parametrize("seed", [16, 17])
def test_random_data(run, same, data, seed):
    _u, _e, o = data(seed, 80)
    _, rows = run(QUERY, orders=o)
    assert same(rows, truth(o)), "Complete calendar, then running sum and a 7-ROW average on that calendar."
