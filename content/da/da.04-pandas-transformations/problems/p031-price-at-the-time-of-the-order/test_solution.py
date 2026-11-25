import math

import pandas as pd

from solution import price_at_order


def orders():
    return pd.DataFrame({
        "order_id": [5, 1, 3, 2, 4, 6],
        "product_id": ["P1", "P1", "P2", "P1", "P2", "P2"],
        "order_date": pd.to_datetime(["2025-03-15", "2025-01-10", "2025-01-20", "2025-02-01", "2025-04-01", "2025-03-31"]),
        "qty": [1, 2, 1, 1, 3, 2],
    })


def history():
    return pd.DataFrame({
        "product_id": ["P1", "P1", "P2", "P1", "P2"],
        "effective": pd.to_datetime(["2025-01-01", "2025-03-01", "2025-02-01", "2025-02-01", "2025-04-01"]),
        "price": [100.0, 120.0, 50.0, 110.0, 45.0],
    })


def test_row_count_and_order():
    out = price_at_order(orders(), history())
    assert len(out) == 6, "every order line must stay: the row count of an as-of join equals the left table (got %d)" % len(out)
    assert out["order_id"].tolist() == [1, 2, 3, 4, 5, 6], "sort the result by order_id"
    assert out.index.tolist() == list(range(6)), "reset the index after sorting (0, 1, 2, ...)"


def test_columns():
    out = price_at_order(orders(), history())
    assert list(out.columns) == ["order_id", "product_id", "order_date", "qty", "price"], (
        "keep the order columns and add only `price` (drop the helper column `effective`); got %s" % list(out.columns))


def test_prices():
    out = price_at_order(orders(), history()).set_index("order_id")["price"]
    assert out[1] == 100.0, "order 1 (10 Jan) uses the January price 100"
    assert out[2] == 110.0, "order 2 is ON the day the price 110 starts: a price that starts on the order day counts (backward includes equal)"
    assert out[5] == 120.0, "order 5 (15 Mar) uses the latest earlier price, 120 from 1 Mar"
    assert out[6] == 50.0, "order 6 (31 Mar, P2) uses 50: the price 45 only starts on 1 Apr (did you use direction='forward' or 'nearest'?)"
    assert out[4] == 45.0, "order 4 (1 Apr, P2) uses the new price 45 that starts that day"


def test_before_first_price_is_missing_and_products_do_not_mix():
    out = price_at_order(orders(), history()).set_index("order_id")["price"]
    if out[3] == 100.0:
        raise AssertionError("order 3 is for P2 but got P1's price 100: add by='product_id' so prices are matched per product")
    assert math.isnan(out[3]), "order 3 (P2 on 20 Jan) is before P2's first price (1 Feb): its price must be NaN, not filled"


def test_inputs_unchanged():
    o, h = orders(), history()
    o0, h0 = o.copy(), h.copy()
    price_at_order(o, h)
    pd.testing.assert_frame_equal(o, o0, obj="orders (sort a copy, never the input in place)")
    pd.testing.assert_frame_equal(h, h0, obj="price_history (sort a copy, never the input in place)")


def test_already_sorted_input_gives_same_answer():
    o = orders().sort_values("order_date")
    h = history().sort_values("effective")
    a = price_at_order(o, h)
    b = price_at_order(orders(), history())
    pd.testing.assert_frame_equal(a, b, obj="the answer must not depend on the input order")
