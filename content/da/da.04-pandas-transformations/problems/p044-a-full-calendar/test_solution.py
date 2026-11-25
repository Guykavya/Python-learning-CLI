import math

import pandas as pd
import pytest

from solution import daily_sales


def orders():
    return pd.DataFrame({
        "order_id": [10, 11, 12, 13, 14, 15],
        "order_date": pd.to_datetime(["2025-03-03", "2025-03-01", "2025-02-27", "2025-03-06", "2025-03-01", "2025-03-08"]),
        "revenue": [20.0, 100.0, 999.0, 10.0, 50.0, 7.0],
    })


def days(out):
    return out["date"].dt.strftime("%Y-%m-%d").tolist()


def test_columns_and_day_count():
    out = daily_sales(orders(), "2025-03-01", "2025-03-07")
    assert list(out.columns) == ["date", "revenue"], "the columns are date and revenue; got %s" % list(out.columns)
    assert len(out) == 7, "1 to 7 March is 7 days, both ends included: one row per calendar day (got %d)" % len(out)


def test_every_day_in_order():
    out = daily_sales(orders(), "2025-03-01", "2025-03-07")
    assert days(out) == ["2025-03-%02d" % d for d in range(1, 8)], (
        "one row per day in order, including days without orders; got %s" % days(out))


def test_values():
    out = daily_sales(orders(), "2025-03-01", "2025-03-07")
    rev = out["revenue"].tolist()
    assert not any(isinstance(v, float) and math.isnan(v) for v in rev), "days without orders must be 0.0, not NaN (fill_value=0.0)"
    assert rev == pytest.approx([150.0, 0.0, 20.0, 0.0, 0.0, 10.0, 0.0]), (
        "1 March has two orders (100 + 50); 2, 4, 5, 7 March have none; got %s" % rev)


def test_orders_outside_are_ignored():
    out = daily_sales(orders(), "2025-03-01", "2025-03-07")
    assert out["revenue"].sum() == pytest.approx(180.0), (
        "the orders of 27 Feb (999) and 8 March (7) are outside the period and must not be counted")


def test_period_before_the_first_order():
    out = daily_sales(orders(), "2025-02-25", "2025-02-28")
    assert days(out) == ["2025-02-25", "2025-02-26", "2025-02-27", "2025-02-28"], (
        "the calendar must start at `start` even if there is no order that day (asfreq cannot do that)")
    assert out["revenue"].tolist() == pytest.approx([0.0, 0.0, 999.0, 0.0])


def test_single_day():
    out = daily_sales(orders(), "2025-03-06", "2025-03-06")
    assert days(out) == ["2025-03-06"] and out["revenue"].tolist() == pytest.approx([10.0]), "start == end is one day"


def test_input_unchanged():
    o = orders()
    before = o.copy()
    daily_sales(o, "2025-03-01", "2025-03-07")
    pd.testing.assert_frame_equal(o, before, obj="orders")
