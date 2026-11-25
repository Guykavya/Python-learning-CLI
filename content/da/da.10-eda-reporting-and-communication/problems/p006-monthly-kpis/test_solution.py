import numpy as np
import pandas as pd
import pytest

from solution import monthly_kpis

CUS = pd.DataFrame({"customer_id": [1, 2, 3, 4],
                    "last_week": pd.to_datetime(["2024-01-15", pd.NaT, "2024-02-05", "2024-01-15"])})
PAN = pd.DataFrame({
    "customer_id": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4],
    "week": pd.to_datetime(["2024-01-01", "2024-01-08", "2024-01-15", "2024-01-01", "2024-01-08", "2024-02-05",
                            "2024-01-01", "2024-01-08", "2024-02-05", "2024-01-15"]),
    "late": [False, True, False, False, False, False, False, False, True, False],
    "price": [100, 100, 100, 200, 200, 200, 100, 100, 100, 100],
})


def k():
    return monthly_kpis(CUS, PAN)


def test_columns_and_index():
    out = k()
    assert list(out.columns) == ["opening_actives", "churned", "churn_rate_pct", "on_time_pct", "weekly_revenue_k"], f"columns in the given order, got {list(out.columns)}"
    assert list(out.index.astype(str)) == ["2024-01", "2024-02"], "one row per month, indexed by Period."


def test_january():
    jan = k().loc[pd.Period("2024-01")]
    assert jan["opening_actives"] == 3, f"customers 1, 2, 3 had a box on 1 January (customer 4 joined later): 3, got {jan['opening_actives']}"
    assert jan["churned"] == 1, f"only customer 1 is an opening active whose last week is in January (4 was not active at the start, 3 leaves in February), got {jan['churned']}"
    assert jan["churn_rate_pct"] == pytest.approx(100 / 3), "1 of 3 = 33.3%"
    assert jan["on_time_pct"] == pytest.approx((1 - 1 / 8) * 100), "1 late box out of 8 January rows: 87.5% on time"


def test_weekly_revenue():
    jan = k().loc[pd.Period("2024-01")]
    assert jan["weekly_revenue_k"] == pytest.approx((400 + 400 + 200) / 3 / 1000), "sum the prices per week (400, 400, 200), average the weeks, divide by 1,000."


def test_february():
    feb = k().loc[pd.Period("2024-02")]
    assert feb["opening_actives"] == 2 and feb["churned"] == 1, "February: customers 2 and 3 open the month, customer 3 leaves in it."
    assert feb["churn_rate_pct"] == pytest.approx(50.0)
    assert feb["on_time_pct"] == pytest.approx(50.0), "one of the two February boxes was late."
