import math

import pandas as pd
import pytest

from solution import rolling_week

# Expected values worked out by hand from the calendar (window = date-6 .. date):
#  1 Mar: 10                 2 Mar: 10+20 = 30          4 Mar: 10+20+5 = 35
#  8 Mar: 2..8  -> 20+5+40 = 65                         9 Mar: 3..9 -> 5+40+1 = 46
# 15 Mar: 9..15 -> 1+100 = 101                         16 Mar: 10..16 -> 100+7 = 107
DATES = ["2025-03-01", "2025-03-02", "2025-03-04", "2025-03-08", "2025-03-09", "2025-03-15", "2025-03-16"]
REVENUE = [10.0, 20.0, 5.0, 40.0, 1.0, 100.0, 7.0]
WEEK = [10.0, 30.0, 35.0, 65.0, 46.0, 101.0, 107.0]


def daily():
    order = [4, 0, 6, 2, 5, 1, 3]                     # shuffled on purpose
    return pd.DataFrame({"date": pd.to_datetime([DATES[i] for i in order]), "revenue": [REVENUE[i] for i in order]})


def test_columns_and_order():
    out = rolling_week(daily())
    assert list(out.columns) == ["date", "revenue", "week_total"], "columns date, revenue, week_total; got %s" % list(out.columns)
    assert out["date"].dt.strftime("%Y-%m-%d").tolist() == DATES, "rows sorted by date"
    assert out["revenue"].tolist() == REVENUE, "each revenue must stay with its own date"
    assert out.index.tolist() == list(range(7)), "fresh index"


def test_no_missing_values():
    w = rolling_week(daily())["week_total"].tolist()
    assert not any(math.isnan(v) for v in w), (
        "no NaN: the first days sum what they have. NaN in the first 6 rows means rolling(7), a 7-ROW window")


def test_seven_calendar_days():
    w = rolling_week(daily())["week_total"].tolist()
    if w[3] == pytest.approx(75.0):
        pytest.fail("8 March gave 75 = the last 7 ROWS (rolling(7, min_periods=1)). The 7 DAYS 2..8 March hold 20+5+40 = 65: use rolling('7D')")
    assert w[3] == pytest.approx(65.0), "8 March: the window 2..8 March holds 20 + 5 + 40 = 65; got %s" % w[3]
    assert w[5] == pytest.approx(101.0), "15 March: the window 9..15 March holds 1 + 100 = 101; got %s" % w[5]
    assert w == pytest.approx(WEEK), "all week totals (worked out by hand from the calendar); got %s" % w


def test_window_includes_the_day_and_six_before():
    d = pd.DataFrame({"date": pd.to_datetime(["2025-05-01", "2025-05-07", "2025-05-08"]), "revenue": [1.0, 2.0, 4.0]})
    w = rolling_week(d)["week_total"].tolist()
    assert w == pytest.approx([1.0, 3.0, 6.0]), (
        "1 May is inside the window of 7 May (1..7) but outside the window of 8 May (2..8); got %s" % w)


def test_input_unchanged():
    d = daily()
    before = d.copy()
    rolling_week(d)
    pd.testing.assert_frame_equal(d, before, obj="daily (sort a copy)")
