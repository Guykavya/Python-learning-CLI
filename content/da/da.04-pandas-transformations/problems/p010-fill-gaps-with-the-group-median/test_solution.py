import math

import pandas as pd
import pytest

from solution import fill_price_by_category


def products():
    nan = float("nan")
    return pd.DataFrame({
        "product_id": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"],
        "category": ["home", "toys", "home", "office", "home", "toys", "beauty", "home", "office", "toys"],
        "list_price": [100.0, 10.0, nan, nan, 300.0, 30.0, 55.0, 200.0, nan, nan],
    }, index=[11, 12, 13, 14, 15, 16, 17, 18, 19, 20])


def test_shape_and_index_kept():
    df = products()
    filled, _ = fill_price_by_category(df)
    assert list(filled.columns) == ["product_id", "category", "list_price"], "same columns as the input."
    assert filled.index.tolist() == df.index.tolist(), "same rows, same order, same index labels as the input."


def test_gaps_filled_with_own_category_median():
    filled, _ = fill_price_by_category(products())
    p = filled.set_index("product_id")["list_price"]
    assert p["P3"] == pytest.approx(200.0), (
        "P3 (home) gets the median of home's known prices 100, 300, 200 -> 200. The mean would also be 200 here; "
        "the whole-catalogue median would be 77.5. Got %s." % p["P3"])
    assert p["P10"] == pytest.approx(20.0), (
        "P10 (toys) gets the median of 10 and 30 = 20 (the mean of the two middle values). Got %s." % p["P10"])


def test_known_prices_unchanged():
    filled, _ = fill_price_by_category(products())
    p = filled.set_index("product_id")["list_price"]
    for pid, v in [("P1", 100.0), ("P2", 10.0), ("P5", 300.0), ("P6", 30.0), ("P7", 55.0), ("P8", 200.0)]:
        assert p[pid] == v, "%s had a known price %s: fill only the gaps, never change a known value." % (pid, v)


def test_category_without_prices_stays_missing():
    filled, unfilled = fill_price_by_category(products())
    p = filled.set_index("product_id")["list_price"]
    assert math.isnan(p["P4"]) and math.isnan(p["P9"]), (
        "office has no known price, so its median is missing and its gaps stay missing. Do not invent a value "
        "(0, or the overall median) here.")
    assert unfilled == ["office"], "unfilled must list the categories with no known price: ['office']. Got %s." % (unfilled,)


def test_skewed_category_uses_median_not_mean():
    df = pd.DataFrame({"product_id": ["A", "B", "C", "D"], "category": ["x"] * 4, "list_price": [10.0, 12.0, 1000.0, None]})
    filled, unfilled = fill_price_by_category(df)
    assert filled["list_price"].tolist()[3] == pytest.approx(12.0), (
        "the median of 10, 12, 1000 is 12; the mean (340.7) is pulled up by the outlier. Use 'median'.")
    assert unfilled == []


def test_input_not_changed():
    df = products()
    before = df.copy()
    fill_price_by_category(df)
    pd.testing.assert_frame_equal(df, before, obj="the input products")
