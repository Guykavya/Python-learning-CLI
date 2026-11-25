import csv

import pandas as pd
import pytest

from solution import load_sales

ROWS = [
    ["id", "when", "who", "price", "paid", "qty"],
    ["1", "2025-03-01", " asha ", "₹1,200.50", "Y", "3"],
    ["2", "02/03/2025", "BEN", "Rs. 80", "no", "2.5"],
    ["3", "Mar 3, 2025", "chitra", "free", "TRUE", "4"],
    ["4", "31/02/2025", "dev", "", "maybe", "x"],
    ["5", "", "esha", "45.25", "", "N/A"],
]


def write(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return path


def plain(values):
    return [None if pd.isna(v) else v for v in values]


@pytest.fixture
def loaded(tmp_path):
    path = write(tmp_path / "sales.csv", ROWS)
    return load_sales(path, money=["price"], dates=["when"], bools=["paid"], ints=["id", "qty"])


def test_returns_a_pair(loaded):
    assert isinstance(loaded, tuple) and len(loaded) == 2, "return a pair (df, losses)."
    df, losses = loaded
    assert isinstance(df, pd.DataFrame) and isinstance(losses, dict), f"expected (DataFrame, dict), got ({type(df).__name__}, {type(losses).__name__})."
    assert df.columns.tolist() == ["id", "when", "who", "price", "paid", "qty"], f"keep the column order; got {df.columns.tolist()}."
    assert len(df) == 5, f"five data rows, got {len(df)}."


def test_money(loaded):
    df, _ = loaded
    assert pd.api.types.is_numeric_dtype(df["price"].dtype), f"price must be numeric, got {df['price'].dtype}."
    assert plain(df["price"]) == [1200.5, 80.0, None, None, 45.25], (
        f"price: ₹1,200.50, Rs. 80, 'free' (missing), '' (missing), 45.25; got {df['price'].tolist()}.")


def test_dates(loaded):
    df, _ = loaded
    assert str(df["when"].dtype).startswith("datetime64"), f"when must be a datetime column, got {df['when'].dtype}."
    want = [pd.Timestamp("2025-03-01"), pd.Timestamp("2025-03-02"), pd.Timestamp("2025-03-03"), None, None]
    assert plain(df["when"]) == want, (
        f"when: 02/03/2025 is day first (2 March); 31/02/2025 does not exist and '' is empty: both missing. Got {df['when'].tolist()}.")


def test_bools(loaded):
    df, _ = loaded
    assert str(df["paid"].dtype) == "boolean", f"paid must have the nullable dtype 'boolean', got {df['paid'].dtype}."
    assert plain(df["paid"]) == [True, False, True, None, None], f"paid: Y, no, TRUE, 'maybe' (missing), '' (missing); got {df['paid'].tolist()}."


def test_ints(loaded):
    df, _ = loaded
    assert str(df["qty"].dtype) == "Int64" and str(df["id"].dtype) == "Int64", f"ints must have dtype Int64, got {df['id'].dtype} and {df['qty'].dtype}."
    assert plain(df["qty"]) == [3, None, 4, None, None], f"qty: 3, 2.5 (not whole), 4, x, N/A; got {df['qty'].tolist()}."
    assert plain(df["id"]) == [1, 2, 3, 4, 5], f"id: got {df['id'].tolist()}."


def test_unconverted_columns_stay_text_exactly(loaded):
    df, _ = loaded
    assert df["who"].tolist() == [" asha ", "BEN", "chitra", "dev", "esha"], f"a column named in no group stays exactly as read (do not strip or change it); got {df['who'].tolist()}."
    assert pd.api.types.is_string_dtype(df["who"].dtype), f"who stays text, got {df['who'].dtype}."


def test_losses_count_what_was_given_up(loaded):
    _, losses = loaded
    assert losses == {"price": 1, "when": 1, "paid": 1, "id": 0, "qty": 2}, (
        f"expected {{'price': 1, 'when': 1, 'paid': 1, 'id': 0, 'qty': 2}}, got {losses}. A loss is a raw cell that was NOT missing "
        "(the empty cells and N/A were already missing) but whose converted value is missing: 'free'; 31/02/2025; 'maybe'; '2.5' and 'x'.")


def test_nothing_named_means_everything_stays_text(tmp_path):
    path = write(tmp_path / "plain.csv", ROWS)
    df, losses = load_sales(path)
    assert losses == {}, f"no converted columns: losses is empty, got {losses}."
    assert df["id"].tolist() == ["1", "2", "3", "4", "5"], "with no groups named, id stays the text '1' ... '5'."
    assert all(pd.api.types.is_string_dtype(df[c].dtype) for c in df.columns), "every column is text when nothing is converted."


def test_a_clean_file_loses_nothing(tmp_path):
    rows = [["when", "price", "paid", "n"], ["2025-01-02", "Rs. 1,000", "yes", "7"], ["01/02/2025", "5", "N", "8"], ["Feb 3, 2025", "INR 2,50,000", "1", "9"]]
    df, losses = load_sales(write(tmp_path / "clean.csv", rows), money=["price"], dates=["when"], bools=["paid"], ints=["n"])
    assert losses == {"price": 0, "when": 0, "paid": 0, "n": 0}, f"nothing should be lost, got {losses}."
    assert df["price"].tolist() == [1000.0, 5.0, 250000.0], f"got {df['price'].tolist()}."
    assert plain(df["when"]) == [pd.Timestamp("2025-01-02"), pd.Timestamp("2025-02-01"), pd.Timestamp("2025-02-03")], f"got {df['when'].tolist()}."
    assert plain(df["paid"]) == [True, False, True], f"got {df['paid'].tolist()}."
