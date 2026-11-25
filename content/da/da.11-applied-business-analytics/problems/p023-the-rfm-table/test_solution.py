import numpy as np
import pandas as pd
import pytest

from solution import rfm_table

CUS = pd.DataFrame({"customer_id": ["a", "b", "c", "d"]})
ORD = pd.DataFrame([("a", "2024-01-10", 100), ("a", "2024-03-01", 50), ("b", "2024-03-30", 20), ("b", "2024-03-30", 25),
                    ("c", "2024-04-05", 999), ("a", "2024-04-05", 77), ("x", "2024-03-01", 10)],
                   columns=["customer_id", "order_date", "amount"]).assign(order_date=lambda d: pd.to_datetime(d["order_date"]))


def test_hand_values():
    t = rfm_table(ORD, CUS, "2024-03-31")
    assert list(t.columns) == ["R", "F", "M"] and t.index.name == "customer_id", f"columns R, F, M and index customer_id; got {list(t.columns)}, {t.index.name}"
    assert t.loc["a"].tolist() == [30, 2, 150], "a: last order 1 March = 30 days before 31 March, 2 orders, 150 (the April order is ignored)."
    assert t.loc["b"].tolist() == [1, 2, 45], "b: two orders on the same day are two orders."


def test_absent_customers():
    t = rfm_table(ORD, CUS, "2024-03-31")
    assert list(t.index) == ["a", "b"], f"c ordered only after the as-of date, d never, x is not in customers: absent. Got {list(t.index)}"


def test_later_asof_sees_more():
    t = rfm_table(ORD, CUS, "2024-04-30")
    assert t.loc["c"].tolist() == [25, 1, 999] and t.loc["a", "F"] == 3, "as of 30 April the April orders count."


def test_recency_is_an_int():
    assert rfm_table(ORD, CUS, "2024-03-31")["R"].dtype.kind == "i", "R is a whole number of days."
