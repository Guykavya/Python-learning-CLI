import datetime as dt

import pandas as pd

from solution import add_date_parts

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def make():
    days = [dt.datetime(2024, 2, 29, 13, 5), dt.datetime(2025, 1, 1), dt.datetime(2025, 3, 1), dt.datetime(2025, 3, 2),
            dt.datetime(2025, 3, 3), dt.datetime(2025, 12, 31, 23, 59), None, dt.datetime(2025, 4, 1)]
    return pd.DataFrame({"id": range(len(days)), "when": pd.to_datetime(days), "other": list("abcdefgh")})


def test_columns_and_input():
    df = make()
    before = df.copy()
    out = add_date_parts(df, "when")
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
    assert isinstance(out, pd.DataFrame), f"return a DataFrame, not a {type(out).__name__}."
    assert out.columns.tolist() == ["id", "when", "other", "year", "month", "quarter", "weekday", "is_weekend"], (
        f"the old columns first, then year, month, quarter, weekday, is_weekend; got {out.columns.tolist()}.")
    assert out["other"].tolist() == list("abcdefgh"), "other columns must be kept."


def test_each_part_against_python_datetime():
    out = add_date_parts(make(), "when")
    for i, ts in enumerate(make()["when"]):
        if pd.isna(ts):
            for c in ["year", "month", "quarter", "weekday"]:
                assert pd.isna(out[c].iloc[i]), f"row {i} (NaT): '{c}' should be missing, got {out[c].iloc[i]!r}."
            assert out["is_weekend"].iloc[i] == False, f"row {i} (NaT): is_weekend should be False, got {out['is_weekend'].iloc[i]!r}."
            continue
        d = ts.to_pydatetime()
        assert out["year"].iloc[i] == d.year, f"row {i}: year should be {d.year}, got {out['year'].iloc[i]}."
        assert out["month"].iloc[i] == d.month, f"row {i}: month should be {d.month}, got {out['month'].iloc[i]}."
        assert out["quarter"].iloc[i] == (d.month - 1) // 3 + 1, f"row {i}: quarter should be {(d.month - 1) // 3 + 1}, got {out['quarter'].iloc[i]}."
        assert out["weekday"].iloc[i] == DAYS[d.weekday()], f"row {i}: weekday should be {DAYS[d.weekday()]!r}, got {out['weekday'].iloc[i]!r}."
        assert bool(out["is_weekend"].iloc[i]) == (d.weekday() >= 5), (
            f"row {i} ({DAYS[d.weekday()]}): is_weekend should be {d.weekday() >= 5}. Monday is 0 in day_of_week, so weekend is >= 5.")


def test_weekend_is_a_real_boolean_column():
    out = add_date_parts(make(), "when")
    assert str(out["is_weekend"].dtype) == "bool", f"is_weekend should have dtype bool, got {out['is_weekend'].dtype}."


def test_column_name_is_a_parameter():
    df = pd.DataFrame({"shipped": pd.to_datetime(["2025-06-14", "2025-06-16"])})
    out = add_date_parts(df, "shipped")
    assert out["weekday"].tolist() == ["Saturday", "Monday"] and out["is_weekend"].tolist() == [True, False], (
        f"use the column named by `col`, not a fixed name. Got {out['weekday'].tolist()} / {out['is_weekend'].tolist()}.")
