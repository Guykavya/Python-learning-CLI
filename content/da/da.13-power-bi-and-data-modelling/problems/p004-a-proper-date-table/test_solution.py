import numpy as np
import pandas as pd
import pytest

from solution import date_table


def test_leap_year_hand_case():
    t = date_table("2024-02-27", "2024-03-02")
    assert list(t.columns) == ["DateKey", "Date", "Year", "Quarter", "MonthNum", "MonthName", "YearMonth"], f"columns, got {list(t.columns)}"
    assert t["DateKey"].tolist() == [20240227, 20240228, 20240229, 20240301, 20240302], f"2024 is a leap year; got {t['DateKey'].tolist()}"
    assert t["MonthName"].tolist() == ["Feb", "Feb", "Feb", "Mar", "Mar"] and t["YearMonth"].tolist()[-1] == "2024-03"
    assert t["Quarter"].unique().tolist() == ["Q1"] and t["MonthNum"].tolist()[-1] == 3 and t["Year"].iloc[0] == 2024


def test_no_gaps_unique_and_integer_key():
    t = date_table("2023-01-01", "2025-12-31")
    assert len(t) == 1096 and t["Date"].is_unique and t["DateKey"].is_unique, "1,096 days in 2023 to 2025, one row each."
    assert (t["Date"].diff().dropna() == pd.Timedelta(days=1)).all(), "no gaps."
    assert t["DateKey"].dtype.kind == "i" and t["Year"].dtype.kind == "i", "integer keys."


def test_covers_the_facts_at_both_ends():
    facts = pd.DataFrame({"OrderDate": pd.to_datetime(["2023-01-01", "2024-07-15", "2025-12-31"])})
    t = date_table(facts["OrderDate"].min(), facts["OrderDate"].max())
    keys = facts["OrderDate"].dt.strftime("%Y%m%d").astype(int)
    assert keys.isin(t["DateKey"]).all(), "every fact date, including the first and the last, is in the date table."


def test_single_day_and_reversed_range():
    assert len(date_table("2024-05-05", "2024-05-05")) == 1, "start == end is one day."
    with pytest.raises(ValueError, match="end is before start"):
        date_table("2024-05-06", "2024-05-05")
