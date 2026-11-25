import numpy as np
import pandas as pd
import pytest

from solution import revenue_tree

SMALL = pd.DataFrame({"month": ["2024-02", "2024-01", "2024-01", "2024-01"], "customer_id": ["a", "a", "a", "b"], "amount": [50.0, 10.0, 20.0, 30.0]})


def test_hand_example():
    t = revenue_tree(SMALL)
    assert list(t.columns) == ["active", "orders_per_active", "avg_order_value", "revenue"], f"columns, got {list(t.columns)}"
    assert list(t.index) == ["2024-01", "2024-02"], "one row per month, sorted."
    jan = t.loc["2024-01"]
    assert jan["active"] == 2, "January has 2 distinct customers (count customers, not orders)."
    assert jan["orders_per_active"] == pytest.approx(1.5) and jan["avg_order_value"] == pytest.approx(20.0) and jan["revenue"] == pytest.approx(60.0)
    feb = t.loc["2024-02"]
    assert (feb["active"], feb["orders_per_active"], feb["avg_order_value"], feb["revenue"]) == (1, 1.0, 50.0, 50.0)


def test_the_tree_multiplies_back_to_revenue():
    rng = np.random.default_rng(0)
    n = 500
    orders = pd.DataFrame({"month": rng.choice(["2024-01", "2024-02", "2024-03", "2024-04"], n),
                           "customer_id": rng.integers(0, 120, n), "amount": rng.gamma(3, 15, n).round(2)})
    t = revenue_tree(orders)
    for month, row in t.iterrows():
        product = row["active"] * row["orders_per_active"] * row["avg_order_value"]
        assert abs(product - row["revenue"]) < 1e-9 * max(1.0, row["revenue"]), f"{month}: active x orders per active x AOV = {product}, revenue = {row['revenue']}"
        assert row["revenue"] == pytest.approx(orders.loc[orders["month"] == month, "amount"].sum())
