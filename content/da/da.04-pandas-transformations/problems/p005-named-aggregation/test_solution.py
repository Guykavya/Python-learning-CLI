import pandas as pd
import pytest

from solution import store_summary


def lines():
    return pd.DataFrame({
        "order_id": [1, 1, 2, 3, 4, 4, 4, 5],
        "store_id": ["S1", "S1", "S1", "S2", "S2", "S2", "S2", "S3"],
        "product_id": ["P1", "P2", "P1", "P3", "P1", "P2", "P3", "P2"],
        "qty": [2, 1, 1, 3, 2, 2, 1, 4],
        "unit_price": [10.0, 5.5, 10.0, 4.0, 9.0, 5.5, 4.0, 5.0],
    })


def result(df=None):
    out = store_summary(lines() if df is None else df)
    assert list(out.columns) == ["store_id", "orders", "revenue", "units"], (
        "columns must be exactly store_id, orders, revenue, units. Got %s. Use named aggregation "
        "agg(orders=(...), revenue=(...), units=(...)) with as_index=False." % list(out.columns))
    return out


def test_one_row_per_store_sorted():
    out = result()
    assert out["store_id"].tolist() == ["S1", "S2", "S3"], "one row per store, sorted by store_id."
    assert out.index.tolist() == [0, 1, 2], "flat result with index 0..n-1."


def test_orders_are_distinct_orders_not_lines():
    assert result()["orders"].tolist() == [2, 2, 1], (
        "orders = DIFFERENT order ids per store (nunique). S2 has 4 lines but only 2 orders (3 and 4). "
        "size() or count() would count lines.")


def test_revenue_is_sum_of_qty_times_price():
    got = result()["revenue"].tolist()
    assert got == pytest.approx([35.5, 45.0, 20.0]), (
        "revenue = sum of qty * unit_price per line. S2: 3*4.0 + 2*9.0 + 2*5.5 + 1*4.0 = 45.0. "
        "sum(qty) * sum(unit_price) would be 8 * 22.5 = 180. Got %s." % got)


def test_units_is_total_qty():
    assert result()["units"].tolist() == [4, 8, 4], "units = sum of qty per store."


def test_revenue_adds_up():
    df = lines()
    assert result(df)["revenue"].sum() == pytest.approx((df["qty"] * df["unit_price"]).sum()), (
        "the store revenues must add up to the revenue of the whole table.")


def test_input_not_changed():
    df = lines()
    before = df.copy()
    store_summary(df)
    pd.testing.assert_frame_equal(df, before, obj="the input lines (build revenue with assign, on a new frame)")
