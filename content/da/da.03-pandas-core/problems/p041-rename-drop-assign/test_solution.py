import pandas as pd

from solution import prepare


def make():
    return pd.DataFrame(
        {" Order ID": [1, 2, 3], "Unit Price ": [250.0, 80.5, 10.0], "QTY": [2, 5, 0], "Ship  City": ["Pune", "Agra", "Surat"],
         "TMP_note": ["a", "b", "c"], "tmp_flag": [True, False, True]},
        index=[10, 20, 30])


def test_columns_and_values():
    df = make()
    before = df.copy()
    out = prepare(df)
    assert isinstance(out, pd.DataFrame), f"return a DataFrame, not a {type(out).__name__}."
    assert out.columns.tolist() == ["order_id", "unit_price", "qty", "ship__city", "revenue"], (
        f"expected ['order_id', 'unit_price', 'qty', 'ship__city', 'revenue'], got {out.columns.tolist()}. "
        "Strip and lower-case each name and replace each space by '_' (two spaces give two underscores); "
        "drop names starting with 'tmp_' after renaming (TMP_note and tmp_flag).")
    assert out["revenue"].tolist() == [500.0, 402.5, 0.0], f"revenue = qty * unit_price, got {out['revenue'].tolist()}."
    assert out.index.tolist() == [10, 20, 30], "keep the original index."
    assert out["order_id"].tolist() == [1, 2, 3] and out["ship__city"].tolist() == ["Pune", "Agra", "Surat"], "the other columns must keep their values."
    pd.testing.assert_frame_equal(df, before, obj="the input frame (it must not change)")


def test_revenue_comes_last_and_dtypes_kept():
    out = prepare(make())
    assert out.columns[-1] == "revenue", "revenue must be the last column."
    assert str(out["qty"].dtype) == "int64" and str(out["unit_price"].dtype) == "float64", "do not change the dtypes of the kept columns."


def test_frame_without_tmp_columns():
    df = pd.DataFrame({"Qty": [1, 2], "Unit Price": [3.0, 4.0]})
    out = prepare(df)
    assert out.columns.tolist() == ["qty", "unit_price", "revenue"], f"nothing to drop here; got {out.columns.tolist()}."
    assert out["revenue"].tolist() == [3.0, 8.0], f"got {out['revenue'].tolist()}."
