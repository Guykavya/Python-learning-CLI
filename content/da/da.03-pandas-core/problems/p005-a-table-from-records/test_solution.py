import pandas as pd
import pytest

from solution import orders_frame

COLS = ["order_id", "customer", "order_date", "qty", "price"]

RECORDS = [
    {"order_id": 1, "customer": "Asha", "order_date": "2024-03-05", "qty": 2, "price": 9.5},
    {"order_id": 2, "customer": "Ben", "price": 4.0},
    {"order_id": 3, "customer": "Chen", "order_date": "2024-03-07", "qty": 5},
    {"price": 1.0, "qty": 1, "order_id": 4, "customer": "Dia", "order_date": "2024-03-08"},
]


def test_columns_in_fixed_order():
    df = orders_frame(RECORDS)
    assert df.columns.tolist() == COLS, "columns must be exactly %s in that order (pass columns= or reorder), got %s." % (COLS, df.columns.tolist())
    assert len(df) == 4


def test_values_and_missing_cells():
    df = orders_frame(RECORDS)
    assert df["order_id"].tolist() == [1, 2, 3, 4]
    assert df["customer"].tolist() == ["Asha", "Ben", "Chen", "Dia"]
    assert df["qty"].isna().tolist() == [False, True, False, False], "a record without 'qty' must give a missing qty."
    assert [None if pd.isna(v) else int(v) for v in df["qty"]] == [2, None, 5, 1]
    assert df["price"].isna().tolist() == [False, False, True, False], "a record without 'price' must give a missing price."
    assert df["price"].dropna().tolist() == [9.5, 4.0, 1.0]
    assert df["order_date"].isna().tolist() == [False, True, False, False], "a record without a date gives NaT."


def test_dtypes():
    df = orders_frame(RECORDS)
    assert str(df["order_id"].dtype) == "int64", "order_id dtype is %s, expected int64." % df["order_id"].dtype
    assert str(df["customer"].dtype) == "str", "customer dtype is %s, expected str (text)." % df["customer"].dtype
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"]), "order_date must be parsed with pd.to_datetime, dtype is %s." % df["order_date"].dtype
    assert str(df["qty"].dtype) == "Int64", "qty dtype is %s; use the nullable 'Int64' so the integers survive the gap." % df["qty"].dtype
    assert str(df["price"].dtype) == "float64", "price dtype is %s, expected float64." % df["price"].dtype


def test_dates_are_parsed_correctly():
    df = orders_frame(RECORDS)
    assert df["order_date"].iloc[0] == pd.Timestamp("2024-03-05")
    assert df["order_date"].iloc[3] == pd.Timestamp("2024-03-08"), "key order inside a dict must not matter."


def test_all_complete_records_keep_qty_values():
    df = orders_frame([RECORDS[0], RECORDS[3]])
    assert df["qty"].tolist() == [2, 1]
    assert df.index.tolist() == [0, 1]


def test_empty_list():
    df = orders_frame([])
    assert df.columns.tolist() == COLS, "an empty list still gives the five columns."
    assert len(df) == 0


def test_input_not_changed():
    import copy
    before = copy.deepcopy(RECORDS)
    orders_frame(RECORDS)
    assert RECORDS == before, "the list of dicts must not be modified."
