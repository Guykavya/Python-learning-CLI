import pandas as pd

from solution import customer_counts


def lines():
    return pd.DataFrame({
        "customer_id": ["C", "A", "B", "A", "C", "C", "B", "C", "A", "D", "C"],
        "order_id": [5, 1, 3, 1, 5, 6, 4, 6, 2, 7, 8],
        "product_id": ["P1", "P1", "P3", "P2", "P2", "P3", "P3", "P4", "P1", "P2", None],
        "coupon": ["NEW", "SAVE10", None, "SAVE10", None, "NEW", None, None, None, None, None],
    })


def result():
    out = customer_counts(lines())
    assert list(out.columns) == ["customer_id", "lines", "with_coupon", "distinct_products"], (
        "columns must be customer_id, lines, with_coupon, distinct_products (in that order). Got %s. "
        "Named aggregation with as_index=False gives exactly these." % list(out.columns))
    assert out["customer_id"].tolist() == ["A", "B", "C", "D"], "one row per customer, sorted by customer_id."
    return out


def test_lines_counts_every_row():
    assert result()["lines"].tolist() == [3, 2, 5, 1], (
        "lines = rows per customer: use size(). C has 5 rows, one with a missing product and three without a coupon; "
        "count() of a column would skip missing values.")


def test_with_coupon_skips_missing():
    assert result()["with_coupon"].tolist() == [2, 0, 2, 0], (
        "with_coupon = lines whose coupon is not missing: count() on the coupon column. size() would count every row, "
        "nunique() would count different codes (C used NEW twice: 2 lines, 1 code).")


def test_distinct_products_counts_each_product_once():
    assert result()["distinct_products"].tolist() == [2, 1, 4, 1], (
        "distinct_products = nunique() of product_id: A bought P1 twice (2 different products, not 3); "
        "B bought P3 twice; C's missing product does not count.")


def test_index_and_integer_counts():
    out = result()
    assert out.index.tolist() == [0, 1, 2, 3], "flat result with index 0..n-1 (as_index=False or reset_index())."
    for col in ["lines", "with_coupon", "distinct_products"]:
        assert pd.api.types.is_integer_dtype(out[col]), "%s holds counts: it should be an integer column." % col


def test_lines_add_up_to_the_table():
    df = lines()
    assert customer_counts(df)["lines"].sum() == len(df), "the line counts of all customers must add up to len(lines)."


def test_input_not_changed():
    df = lines()
    before = df.copy()
    customer_counts(df)
    pd.testing.assert_frame_equal(df, before, obj="the input lines")
