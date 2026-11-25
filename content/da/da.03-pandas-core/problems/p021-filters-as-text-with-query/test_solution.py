import inspect

import pandas as pd

import solution
from solution import query_orders


def frame():
    return pd.DataFrame({
        "order id": [1, 2, 3, 4, 5, 6],
        "region": ["N", "S", "N", "N", "S", "N"],
        "qty": [5, 9, 2, 7, 5, 6],
        "unit price": [10.0, 4.0, 3.0, 0.0, 2.5, 8.0],
    }, index=[20, 21, 22, 23, 24, 25])


def slow(df, min_qty, region):
    return [label for label, row in zip(df.index, df.to_dict("records"))
            if row["qty"] >= min_qty and row["region"] == region and row["unit price"] > 0]


def test_example():
    out = query_orders(frame(), 5, "N")
    assert out["order id"].tolist() == [1, 6], "expected order ids [1, 6]; got %s. Row 4 has price 0, row 3 is too small." % out["order id"].tolist()


def test_python_variables_with_at_sign():
    df = frame()
    for min_qty in (0, 5, 6, 10):
        for region in ("N", "S", "W"):
            assert query_orders(df, min_qty, region).index.tolist() == slow(df, min_qty, region), (
                "min_qty=%s region=%s differs from the loop version. Use @min_qty and @region inside the query text." % (min_qty, region))


def test_column_with_a_space_needs_backticks():
    out = query_orders(frame(), 0, "S")
    assert out.index.tolist() == [21, 24], "unit price > 0 must be part of the filter: write `unit price` in backticks."


def test_original_labels_and_columns_kept():
    out = query_orders(frame(), 5, "N")
    assert out.index.tolist() == [20, 25], "the result keeps the original index labels."
    assert out.columns.tolist() == ["order id", "region", "qty", "unit price"]


def test_it_really_uses_query():
    source = inspect.getsource(solution.query_orders)
    assert ".query(" in source, "the task asks for df.query(...) (section 8.4)."


def test_input_not_changed():
    df = frame()
    before = df.copy()
    query_orders(df, 5, "N")
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
