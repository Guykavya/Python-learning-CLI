import pandas as pd
import pytest

from solution import share_of_store


def lines():
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 6, 7, 8],
        "store_id": ["S2", "S1", "S3", "S1", "S2", "S1", "S2", "S3"],
        "revenue": [20.0, 25.0, 9.0, 50.0, 30.0, 25.0, 50.0, 1.0],
    }, index=[40, 41, 42, 43, 50, 51, 52, 53])


def test_has_share_column_and_keeps_rows():
    df = lines()
    out = share_of_store(df)
    assert "share" in out.columns, "add a column named share."
    assert len(out) == len(df), (
        "transform keeps one value per ORIGINAL row: the result has as many rows as the input. "
        "agg('sum') would give one row per store.")
    assert out.index.tolist() == df.index.tolist(), "same rows, same order, same index labels as the input."
    assert list(out.columns) == ["order_id", "store_id", "revenue", "share"], "keep every input column, then add share."


def test_share_values():
    got = share_of_store(lines())["share"].tolist()
    want = [0.2, 0.25, 0.9, 0.5, 0.3, 0.25, 0.5, 0.1]
    assert got == pytest.approx(want), (
        "share = revenue / total of the line's OWN store (S1 = 100, S2 = 100, S3 = 10). Dividing by the grand total "
        "(210) is the share of the whole shop. Got %s." % got)


def test_shares_add_to_one_per_store():
    out = share_of_store(lines())
    sums = out.groupby("store_id")["share"].sum()
    assert sums.tolist() == pytest.approx([1.0, 1.0, 1.0]), "in each store the shares must add up to 1."


def test_input_not_changed():
    df = lines()
    before = df.copy()
    out = share_of_store(df)
    pd.testing.assert_frame_equal(df, before, obj="the input lines (return a new frame; assign or copy first)")
    assert out is not df, "return a new frame."
