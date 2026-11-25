import numpy as np
import pandas as pd
import pytest

from solution import segment_table


def rows(month, channel, n, churned):
    return [{"month": pd.Period(month, "M"), "channel": channel, "churned": i < churned} for i in range(n)]


def make(extra=()):
    r = (rows("2024-01", "paid", 4, 1) + rows("2024-02", "organic", 6, 0)
         + rows("2024-03", "paid", 5, 2) + rows("2024-04", "organic", 5, 1)
         + rows("2024-06", "paid", 7, 7))                                   # outside both periods: ignored
    for e in extra:
        r += e
    return pd.DataFrame(r)


BEFORE, AFTER = ("2024-01", "2024-02"), ("2024-03", "2024-04")


def test_columns_order_and_sorting():
    t = segment_table(make(), "channel", BEFORE, AFTER)
    assert list(t.columns) == ["before share %", "after share %", "before churn %", "after churn %", "change (points)"], f"columns, got {list(t.columns)}"
    assert list(t.index) == ["organic", "paid"], f"sorted by change, largest first: organic (+20) then paid (+15), got {list(t.index)}"
    assert t.index.name == "channel"


def test_hand_values():
    t = segment_table(make(), "channel", BEFORE, AFTER)
    assert t.loc["paid"].tolist() == pytest.approx([40.0, 50.0, 25.0, 40.0, 15.0]), f"paid row, got {t.loc['paid'].tolist()}"
    assert t.loc["organic"].tolist() == pytest.approx([60.0, 50.0, 0.0, 20.0, 20.0]), f"organic row, got {t.loc['organic'].tolist()}"


def test_rows_outside_the_periods_are_ignored():
    t = segment_table(make(), "channel", BEFORE, AFTER)
    assert t.loc["paid", "after churn %"] == pytest.approx(40.0), "June rows are outside both periods: do not count them."


def test_segment_in_one_period_only_is_dropped_but_counts_in_shares():
    t = segment_table(make(extra=[rows("2024-03", "referral", 1, 0)]), "channel", BEFORE, AFTER)
    assert "referral" not in t.index, "a segment that appears only after has no before value: drop it (no NaN)."
    assert not t.isna().any().any(), "the table must be NaN-free."
    assert t.loc["paid", "after share %"] == pytest.approx(500 / 11), "shares are out of ALL rows of the period (11 after rows)."
