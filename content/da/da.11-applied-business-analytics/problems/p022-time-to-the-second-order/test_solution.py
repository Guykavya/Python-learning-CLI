import numpy as np
import pandas as pd
import pytest

from solution import days_to_second


def orders(rows):
    return pd.DataFrame(rows, columns=["customer_id", "order_date"]).assign(order_date=lambda d: pd.to_datetime(d["order_date"]))


ORD = orders([("a", "2024-03-01"), ("a", "2024-03-31"), ("a", "2024-06-09"), ("b", "2024-03-06"),
              ("c", "2024-03-08"), ("c", "2024-03-08"), ("d", "2024-02-01"), ("d", "2024-04-01")])


def test_days_and_counts():
    r = days_to_second(ORD)
    assert r["days"].to_dict() == {"a": 30, "c": 0, "d": 60}, f"a: 30 days to the second order, c: same day = 0, d: 60; got {r['days'].to_dict()}"
    assert r["one_order"] == 1, "only b has a single order."
    assert r["median"] == pytest.approx(30.0), "median of 30, 0, 60."


def test_sorted_and_int():
    r = days_to_second(ORD)
    assert list(r["days"].index) == ["a", "c", "d"] and r["days"].dtype.kind == "i", "indexed by customer id (sorted), integer days."
    assert type(r["one_order"]) is int and type(r["median"]) is float


def test_unsorted_input():
    r = days_to_second(ORD.sample(frac=1, random_state=0))
    assert r["days"].to_dict() == {"a": 30, "c": 0, "d": 60}, "the input order must not matter: sort by date inside."


def test_nobody_reorders():
    r = days_to_second(orders([("a", "2024-03-01"), ("b", "2024-03-02")]))
    assert len(r["days"]) == 0 and r["one_order"] == 2 and np.isnan(r["median"]), "no second orders: empty Series, NaN median."
