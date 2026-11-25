import numpy as np
import pandas as pd
import pytest

from solution import ltv_curve

CUS = pd.DataFrame({"customer_id": ["A", "B", "C"], "first_order": pd.to_datetime(["2024-09-01", "2024-10-01", "2024-11-01"])})
ORD = pd.DataFrame([
    ("A", "2024-09-01", 100), ("A", "2024-09-20", 50), ("A", "2024-10-15", 30), ("A", "2024-11-30", 70),
    ("B", "2024-10-01", 200), ("B", "2024-11-05", 40), ("B", "2024-12-25", 10),
    ("C", "2024-11-01", 500),
], columns=["customer_id", "order_date", "amount"]).assign(order_date=lambda d: pd.to_datetime(d["order_date"]))
ASOF = "2025-01-01"


def test_hand_curve():
    c = ltv_curve(ORD, CUS, ASOF, 2)
    assert c.index.tolist() == [0, 1, 2], "index 0..months."
    assert c.tolist() == pytest.approx([175.0, 210.0, 215.0]), (
        f"two eligible customers (A, B; C has only 61 days): bucket 0 = (100 + 50 + 200) / 2 = 175, then + (30 + 40) / 2, then + 10 / 2; got {c.tolist()}")


def test_recent_customers_and_late_orders_are_ignored():
    c = ltv_curve(ORD, CUS, ASOF, 2)
    assert c.iloc[-1] == pytest.approx(215.0), "C (500 in bucket 0) is not eligible; A's order on day 90 is beyond bucket 2."


def test_cumulative_and_first_point():
    c = ltv_curve(ORD, CUS, ASOF, 2)
    assert (c.diff().dropna() >= 0).all(), "a cumulative curve never decreases."
    c0 = ltv_curve(ORD, CUS, ASOF, 0)
    assert c0.index.tolist() == [0] and c0.iloc[0] == pytest.approx((100 + 50 + 200 + 500) / 3), (
        "with months = 0 all three customers are eligible (29 days of follow-up are enough): (150 + 200 + 500) / 3, the revenue of the first 30 days per customer.")


def test_bigger_horizon_has_fewer_customers():
    c1 = ltv_curve(ORD, CUS, ASOF, 1)
    assert c1.tolist() == pytest.approx([850 / 3, 920 / 3]), f"months = 1 needs 59 days: A, B and C (61 days) are all eligible; got {c1.tolist()}"
    assert ltv_curve(ORD, CUS, ASOF, 2).iloc[0] == pytest.approx(175.0), "months = 2 needs 89 days: C drops out, so the first point changes."


def test_no_eligible_customer():
    with pytest.raises(ValueError, match="no customer has a full follow-up"):
        ltv_curve(ORD, CUS, ASOF, 12)
