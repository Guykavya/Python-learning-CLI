import numpy as np
import pandas as pd
import pytest

from solution import as_of_feature


def test_worked_example():
    events = pd.DataFrame({"customer_id": [1, 1, 1, 1, 2], "day": [3, 9, 10, 15, 1]})
    customers = pd.DataFrame({"customer_id": [1, 2, 3], "predict_day": [10, 5, 7]})
    out = as_of_feature(events, customers)
    assert out.tolist() == [2, 1, 0], "customer 1: days 3 and 9 only (day 10 is ON the prediction day, day 15 is after). Customer 3 has no events: 0."
    assert list(out.index) == [1, 2, 3] and out.name == "events_before", "index = customer_id in the order of customers; name 'events_before'."


def test_planted_future_events_are_ignored():
    rng = np.random.default_rng(0)
    customers = pd.DataFrame({"customer_id": np.arange(50), "predict_day": rng.integers(20, 80, 50)})
    rows = []
    expected = []
    for cid, pday in zip(customers.customer_id, customers.predict_day):
        before = rng.integers(0, 5)
        rows += [(cid, d) for d in rng.integers(0, pday, before)]
        rows += [(cid, pday)] * 2 + [(cid, pday + 1)] * 3            # planted: on and after the date
        expected.append(before)
    events = pd.DataFrame(rows, columns=["customer_id", "day"]).sample(frac=1, random_state=0)
    out = as_of_feature(events, customers)
    assert out.tolist() == expected, "count only events strictly BEFORE each customer's predict_day; events on and after the date are from the future."


def test_integer_values_and_customer_order():
    events = pd.DataFrame({"customer_id": [5, 5], "day": [1, 2]})
    customers = pd.DataFrame({"customer_id": [9, 5], "predict_day": [100, 100]})
    out = as_of_feature(events, customers)
    assert out.tolist() == [0, 2] and out.dtype.kind == "i", "integer counts, in the order of the customers table."
