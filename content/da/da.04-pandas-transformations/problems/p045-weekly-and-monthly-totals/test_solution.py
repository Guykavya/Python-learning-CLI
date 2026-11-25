import pandas as pd
import pytest

from solution import period_totals


def daily():
    """1 Jan 2025 (a Wednesday) to 4 Feb 2025: 1.0 every day, 100.0 on Monday 6 Jan."""
    d = pd.DataFrame({"date": pd.date_range("2025-01-01", "2025-02-04"), "revenue": 1.0})
    d.loc[d["date"] == "2025-01-06", "revenue"] = 100.0
    return d


def labels(out):
    return out["period"].dt.strftime("%Y-%m-%d").tolist()


def call(df, freq):
    try:
        return period_totals(df, freq)
    except ValueError as e:
        if "M" in str(e):
            pytest.fail("pandas 3 removed the alias 'M' (Ch. 9.3): pass freq through unchanged and use 'ME' for months. " + str(e))
        raise


def test_columns():
    out = call(daily(), "ME")
    assert list(out.columns) == ["period", "revenue"], "the columns are period and revenue; got %s" % list(out.columns)
    assert out.index.tolist() == list(range(len(out))), "fresh index"


def test_months():
    out = call(daily(), "ME")
    assert labels(out) == ["2025-01-31", "2025-02-28"], "'ME' bins are labelled by the month's last day; got %s" % labels(out)
    assert out["revenue"].tolist() == pytest.approx([130.0, 4.0]), "January: 30 days x 1.0 + 100.0 = 130; February: 4 days = 4"


def test_weeks_ending_monday():
    out = call(daily(), "W-MON")
    assert labels(out) == ["2025-01-06", "2025-01-13", "2025-01-20", "2025-01-27", "2025-02-03", "2025-02-10"], (
        "W-MON bins are labelled by the Monday that ENDS each week; got %s (plain 'W' would be Sunday weeks)" % labels(out))
    rev = out["revenue"].tolist()
    assert rev[0] == pytest.approx(105.0), (
        "the first week is Wed 1 Jan .. Mon 6 Jan: 5 x 1.0 + the Monday 100.0 = 105 (a Monday belongs to the week it ends)")
    assert rev == pytest.approx([105.0, 7.0, 7.0, 7.0, 7.0, 1.0]), "then full weeks of 7 days, and Tue 4 Feb alone in the last week"


def test_totals_reconcile():
    for freq in ["ME", "W-MON"]:
        assert call(daily(), freq)["revenue"].sum() == pytest.approx(134.0), (
            "every day must fall in exactly one bin: the bins add up to the daily total 134 (%s)" % freq)


def test_old_month_alias_raises():
    with pytest.raises(ValueError):
        period_totals(daily(), "M")


def test_input_unchanged():
    d = daily()
    before = d.copy()
    call(d, "W-MON")
    pd.testing.assert_frame_equal(d, before, obj="daily")
