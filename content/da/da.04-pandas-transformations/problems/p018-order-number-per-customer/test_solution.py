import random

import pandas as pd

from solution import first_orders, number_orders


def orders():
    return pd.DataFrame({
        "order_id": [5, 1, 3, 2, 4, 6],
        "customer_id": ["B", "A", "A", "B", "A", "C"],
        "order_date": pd.to_datetime(["2025-02-01", "2025-01-10", "2025-01-05", "2025-01-20", "2025-01-10", "2025-03-01"]),
    }, index=[10, 11, 12, 13, 14, 15])


def test_number_orders_keeps_row_order_and_index():
    df = orders()
    out = number_orders(df)
    assert out.index.tolist() == df.index.tolist(), (
        "number_orders must keep the input's rows in the same order with the same index. Sort a copy to compute "
        "the numbers, then assign them back: pandas aligns by index label.")
    assert out["order_id"].tolist() == df["order_id"].tolist()
    assert list(out.columns) == ["order_id", "customer_id", "order_date", "order_no"]


def test_order_numbers():
    got = number_orders(orders())["order_no"].tolist()
    assert got == [2, 2, 1, 1, 3, 1], (
        "A: order 3 (Jan 5) is 1st, order 1 (Jan 10) 2nd, order 4 (Jan 10, larger id) 3rd. B: order 2 then 5. "
        "C: order 6. Numbers start at 1 (cumcount() + 1) and follow the DATE, not the row order. Got %s." % got)


def test_same_day_tie_broken_by_order_id():
    out = number_orders(orders()).set_index("order_id")["order_no"]
    assert out[1] == 2 and out[4] == 3, "orders 1 and 4 are on the same day: the smaller id (1) comes first."


def test_order_no_is_integer():
    assert pd.api.types.is_integer_dtype(number_orders(orders())["order_no"]), "order_no must be an integer column."


def test_first_orders():
    out = first_orders(orders())
    assert list(out.columns) == ["order_id", "customer_id", "order_date"], (
        "first_orders returns the input's columns only (drop order_no). Got %s." % list(out.columns))
    assert out["customer_id"].tolist() == ["A", "B", "C"], "one row per customer, sorted by customer_id."
    assert out["order_id"].tolist() == [3, 2, 6], "each customer's EARLIEST order: A -> 3, B -> 2, C -> 6."
    assert out.index.tolist() == [0, 1, 2], "index 0..n-1."


def test_random_against_a_loop():
    rnd = random.Random(4)
    n = 80
    df = pd.DataFrame({
        "order_id": rnd.sample(range(100, 999), n),
        "customer_id": [rnd.choice("WXYZ") for _ in range(n)],
        "order_date": pd.to_datetime("2025-01-01") + pd.to_timedelta([rnd.randint(0, 20) for _ in range(n)], unit="D"),
    }, index=rnd.sample(range(5000), n))
    keyed = sorted(zip(df["customer_id"], df["order_date"], df["order_id"]))
    no, prev, k = {}, None, 0
    for c, _, oid in keyed:
        k = k + 1 if c == prev else 1
        prev = c
        no[oid] = k
    got = number_orders(df)
    assert got["order_no"].tolist() == [no[o] for o in df["order_id"]], "order numbers differ from a plain loop."


def test_input_not_changed():
    df = orders()
    before = df.copy()
    number_orders(df)
    first_orders(df)
    pd.testing.assert_frame_equal(df, before, obj="the input orders")
