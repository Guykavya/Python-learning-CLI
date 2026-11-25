import math

import pandas as pd

from solution import read_shop_csv

TEXT = (
    "order_id;date;customer;qty;price\n"
    "1;05.03.2024;Asha;2;1.250,50\n"
    "2;06.03.2024;Ben;-;9,5\n"
    "3;31.03.2024;Chen;4;-\n"
    "4;01.04.2024;Dia;1;12.000,00\n"
)


def load(tmp_path, text=TEXT):
    path = tmp_path / "shop.csv"
    path.write_text(text, encoding="utf-8", newline="")
    return read_shop_csv(path)


def test_columns_are_split_by_semicolon(tmp_path):
    df = load(tmp_path)
    assert df.columns.tolist() == ["order_id", "date", "customer", "qty", "price"], (
        "got columns %s: the separator is ';' (sep=';')." % df.columns.tolist())
    assert len(df) == 4


def test_decimal_comma_and_thousands_dot(tmp_path):
    df = load(tmp_path)
    assert str(df["price"].dtype) == "float64", (
        "price dtype is %s: use decimal=',' and thousands='.' and na_values=['-'] so '1.250,50' becomes 1250.5." % df["price"].dtype)
    assert df["price"].iloc[0] == 1250.5, "1.250,50 must be 1250.5 (thousands='.', decimal=','), got %r." % df["price"].iloc[0]
    assert df["price"].iloc[1] == 9.5, "9,5 must be 9.5 (decimal=','), got %r." % df["price"].iloc[1]
    assert df["price"].iloc[3] == 12000.0, "12.000,00 must be 12000.0 (thousands='.'), got %r." % df["price"].iloc[3]


def test_dash_means_missing(tmp_path):
    df = load(tmp_path)
    assert math.isnan(df["price"].iloc[2]), "'-' in price must be missing (na_values=['-'])."
    assert math.isnan(df["qty"].iloc[1]), "'-' in qty must be missing (na_values=['-'])."
    assert str(df["qty"].dtype) == "float64", "qty dtype is %s; with the '-' read as missing it becomes float64." % df["qty"].dtype
    assert df["qty"].dropna().tolist() == [2.0, 4.0, 1.0]


def test_dates_are_day_first(tmp_path):
    df = load(tmp_path)
    assert pd.api.types.is_datetime64_any_dtype(df["date"]), "date dtype is %s: use parse_dates=['date']." % df["date"].dtype
    assert df["date"].iloc[0] == pd.Timestamp("2024-03-05"), "05.03.2024 is 5 March, not 3 May: give the format (date_format='%d.%m.%Y')."
    assert df["date"].iloc[2] == pd.Timestamp("2024-03-31")


def test_other_columns(tmp_path):
    df = load(tmp_path)
    assert str(df["order_id"].dtype) == "int64"
    assert df["customer"].tolist() == ["Asha", "Ben", "Chen", "Dia"]


def test_a_second_file_with_a_different_size(tmp_path):
    text = "order_id;date;customer;qty;price\n7;09.12.2023;Eli;3;2,25\n"
    df = load(tmp_path, text)
    assert df["price"].tolist() == [2.25] and df["date"].iloc[0] == pd.Timestamp("2023-12-09")
