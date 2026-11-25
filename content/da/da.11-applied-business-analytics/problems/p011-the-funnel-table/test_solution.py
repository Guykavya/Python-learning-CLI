import numpy as np
import pandas as pd
import pytest

from solution import funnel_table

STEPS = ["viewed", "carted", "bought"]
DF = pd.DataFrame({
    "viewed": [True] * 6 + [False] * 4,
    "carted": [True] * 3 + [False] * 7,
    "bought": [True] + [False] * 9,
})


def test_columns_and_rows():
    t = funnel_table(DF, STEPS)
    assert list(t.columns) == ["step", "sessions", "% of previous step", "% of all sessions", "dropped"], f"columns, got {list(t.columns)}"
    assert list(t["step"]) == ["sessions", "viewed", "carted", "bought"], "one row for all sessions and one per step, in the given order."
    assert list(t.index) == [0, 1, 2, 3]


def test_counts_and_percentages():
    t = funnel_table(DF, STEPS)
    assert list(t["sessions"]) == [10, 6, 3, 1], "10 sessions, 6 viewed, 3 carted, 1 bought."
    assert t["% of previous step"].iloc[1:].tolist() == pytest.approx([60.0, 50.0, 100 / 3]), "each step against the one above it."
    assert t["% of all sessions"].tolist() == pytest.approx([100.0, 60.0, 30.0, 10.0]), "each step against all sessions."


def test_first_row_has_nan_where_there_is_no_previous_step():
    t = funnel_table(DF, STEPS)
    assert pd.isna(t.loc[0, "% of previous step"]) and pd.isna(t.loc[0, "dropped"]), "the first row has no row above: NaN, not 0."
    assert t["dropped"].iloc[1:].tolist() == [4, 3, 2], "dropped = sessions above minus this row."


def test_step_with_zero_sessions():
    df = pd.DataFrame({"a": [True, False], "b": [False, False], "c": [False, False]})
    t = funnel_table(df, ["a", "b", "c"])
    assert t["sessions"].tolist() == [2, 1, 0, 0]
    assert pd.isna(t.loc[3, "% of previous step"]), "no sessions at the previous step: the rate is undefined (NaN), not a crash."
