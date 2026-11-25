import random

import pandas as pd
import pytest

from solution import average_order_value


def lines():
    # S1: four one-line orders of 100.  S2: one order of 600 in two lines.  S3: two orders of 200, three lines.
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 5, 6, 7, 7],
        "store_id": ["S1", "S1", "S1", "S1", "S2", "S2", "S3", "S3", "S3"],
        "qty": [2, 1, 1, 1, 3, 1, 1, 2, 1],
        "unit_price": [50.0, 100.0, 100.0, 100.0, 100.0, 300.0, 200.0, 50.0, 100.0],
    })


def test_overall_is_revenue_over_orders():
    overall, _ = average_order_value(lines())
    assert type(overall) is float, "overall must be a plain Python float: wrap it in float(...)."
    assert overall == pytest.approx(200.0), (
        "overall AOV = total revenue 1400 / 7 different orders = 200. 1400 / 9 lines = 155.6 is the mean LINE "
        "revenue; (100 + 600 + 200) / 3 = 300 is the mean of the store AOVs, which weights a one-order store like a "
        "four-order store. Got %s." % overall)


def test_by_store_columns_and_rows():
    _, by_store = average_order_value(lines())
    assert list(by_store.columns) == ["store_id", "revenue", "orders", "aov"], (
        "by_store columns must be store_id, revenue, orders, aov. Got %s." % list(by_store.columns))
    assert by_store["store_id"].tolist() == ["S1", "S2", "S3"], "one row per store, sorted."
    assert by_store.index.tolist() == [0, 1, 2], "flat result with index 0..n-1."


def test_by_store_values():
    _, by_store = average_order_value(lines())
    assert by_store["revenue"].tolist() == pytest.approx([400.0, 600.0, 400.0]), "revenue per store = sum of qty * unit_price."
    assert by_store["orders"].tolist() == [4, 1, 2], (
        "orders = different order ids (nunique): S2 has 2 lines but 1 order, S3 has 3 lines but 2 orders.")
    assert by_store["aov"].tolist() == pytest.approx([100.0, 600.0, 200.0]), "aov = revenue / orders per store."


def test_overall_is_not_mean_of_store_aovs():
    overall, by_store = average_order_value(lines())
    assert by_store["aov"].mean() != pytest.approx(overall), "on this data the two numbers must differ"
    weighted = (by_store["aov"] * by_store["orders"]).sum() / by_store["orders"].sum()
    assert overall == pytest.approx(weighted), (
        "the overall AOV is the mean of the store AOVs WEIGHTED by each store's number of orders.")


def test_random_against_a_loop():
    rnd = random.Random(5)
    rows = []
    for oid in range(1, 201):
        store = rnd.choice(["S1", "S2", "S3", "S4"])
        for _ in range(rnd.randint(1, 4)):
            rows.append((oid, store, rnd.randint(1, 5), float(rnd.randint(10, 500))))
    df = pd.DataFrame(rows, columns=["order_id", "store_id", "qty", "unit_price"])
    total, orders = 0.0, set()
    for oid, _, q, p in rows:
        total += q * p
        orders.add(oid)
    overall, by_store = average_order_value(df)
    assert overall == pytest.approx(total / len(orders)), "overall AOV differs from a plain loop: total / number of orders."
    assert by_store["orders"].sum() == len(orders), "each order belongs to one store: the store order counts add up."


def test_input_not_changed():
    df = lines()
    before = df.copy()
    average_order_value(df)
    pd.testing.assert_frame_equal(df, before, obj="the input lines")
