import warnings

import pandas as pd
import pytest

from solution import clean


def frame():
    return pd.DataFrame({
        "order_id": [100, 101, 102, 103, 104],
        "qty": [3, -1, 5, -20, 0],
        "price": [1.234, 2.5, None, 3.14159, 10.005],
    }, index=[7, 8, 9, 10, 11])


def call(df):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        try:
            return clean(df)
        except Warning as w:
            pytest.fail("%s: %s. Chained assignment (two brackets before the =) is the bug: use one df.loc[mask, 'col'] = value, or a vectorised assignment." % (type(w).__name__, str(w)[:80]))


def test_negative_quantities_become_zero():
    out = call(frame())
    assert out["qty"].tolist() == [3, 0, 5, 0, 0], (
        "Bug 1: df[mask]['qty'] = 0 changes a temporary, never df. Use out.loc[out['qty'] < 0, 'qty'] = 0. Got %s." % out["qty"].tolist())
    assert str(out["qty"].dtype) == "int64", "qty must stay int64; got %s." % out["qty"].dtype


def test_prices_are_rounded_and_missing_stays_missing():
    out = call(frame())
    prices = out["price"].tolist()
    assert prices[0] == 1.23 and prices[1] == 2.5 and prices[3] == 3.14, (
        "Bug 2: df['price'][i] = ... is chained assignment too. Round the whole column at once: out['price'] = out['price'].round(2). Got %s." % prices)
    assert pd.isna(prices[2]), "a missing price must stay missing."
    assert str(out["price"].dtype) == "float64"


def test_input_is_not_changed():
    df = frame()
    before = df.copy()
    call(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame (make a copy and change the copy)")


def test_result_is_a_new_frame_with_same_labels():
    df = frame()
    out = call(df)
    assert out is not df, "return a new frame, not the input object."
    assert out.index.tolist() == [7, 8, 9, 10, 11], "keep the index labels: a loop over range(len(df)) assumes labels 0, 1, 2, ..."
    assert out.columns.tolist() == ["order_id", "qty", "price"]
    assert out["order_id"].tolist() == [100, 101, 102, 103, 104]


def test_bug3_works_on_a_big_table_quickly():
    n = 100_000
    big = pd.DataFrame({"qty": [(-1) ** i * (i % 7) for i in range(n)], "price": [i / 7 for i in range(n)]})
    out = call(big)
    assert (out["qty"] >= 0).all(), "negative quantities left in a big table."
    assert out["price"].tolist()[:3] == [0.0, 0.14, 0.29], "prices are rounded to 2 decimals."


def test_nothing_to_change():
    df = pd.DataFrame({"qty": [1, 2], "price": [1.5, 2.25]})
    pd.testing.assert_frame_equal(call(df), df, obj="a table that is already clean")
