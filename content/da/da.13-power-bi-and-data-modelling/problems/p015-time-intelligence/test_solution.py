import numpy as np
import pandas as pd
import pytest

from conftest import REVENUE, build_model, flat_of, make_mini
from solution import TIME_MEASURES

T = make_mini(seed=3, n_orders=260)
F = flat_of(T)
MONTHLY = F.groupby(["Year", "Month"])["Revenue"].sum()


def model():
    m = build_model(T)
    m.measure("Revenue", REVENUE)
    for name, expr in TIME_MEASURES.items():
        m.measure(name, expr)
    return m


def month_rev(y, mo):
    return float(MONTHLY[(y, mo)]) if (y, mo) in MONTHLY.index else None


def test_the_three_measures_in_order():
    assert list(TIME_MEASURES) == ["Revenue PY", "Revenue YTD", "YoY %"], f"got {list(TIME_MEASURES)}"


def test_revenue_py_is_the_same_month_last_year():
    m = model()
    for mo in range(1, 13):
        got = m.evaluate("Revenue PY", {"Date[YearMonth]": [f"2024-{mo:02d}"]})
        want = month_rev(2023, mo)
        assert (got is None and want is None) or (got is not None and want is not None and got == pytest.approx(want)), f"2024-{mo:02d}: Revenue PY should be the 2023 month {want}, got {got}."


def test_ytd_is_a_running_sum_that_restarts_in_january():
    m = model()
    for y in (2023, 2024):
        run = 0.0
        for mo in range(1, 13):
            run += month_rev(y, mo) or 0.0
            got = m.evaluate("Revenue YTD", {"Date[YearMonth]": [f"{y}-{mo:02d}"]})
            assert got == pytest.approx(run), f"{y}-{mo:02d}: year to date should be {run:,.2f}, got {got}"


def test_yoy_percent():
    m = model()
    for mo in (1, 6, 12):
        py, cur = month_rev(2023, mo), month_rev(2024, mo)
        got = m.evaluate("YoY %", {"Date[YearMonth]": [f"2024-{mo:02d}"]})
        assert got == pytest.approx((cur - py) / py), f"2024-{mo:02d}: (revenue - PY) / PY"
    assert m.evaluate("YoY %", {"Date[YearMonth]": ["2023-06"]}) is None, "2023 has no previous year in the data: YoY is BLANK."
