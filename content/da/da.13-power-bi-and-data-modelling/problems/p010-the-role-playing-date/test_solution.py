import numpy as np
import pandas as pd
import pytest

from conftest import REVENUE, build_model, flat_of, make_mini
from solution import ship_date_measure


def model():
    t = make_mini(seed=4, n_orders=150)
    # make some orders ship in a later year than they were placed
    s = t["Sales"].copy()
    late = s["OrderDateKey"].between(20241225, 20241231)
    s.loc[late, "ShipDateKey"] = 20250105
    t["Sales"] = s
    m = build_model(t)
    m.measure("Revenue", REVENUE)
    m.measure("Revenue by ship date", ship_date_measure())
    return m, t


def test_ship_date_revenue_matches_pandas_by_year():
    m, t = model()
    f = flat_of(t)
    ship_year = f["ShipDateKey"] // 10000
    for y in (2023, 2024, 2025):
        want = f.loc[ship_year == y, "Revenue"].sum()
        got = m.evaluate("Revenue by ship date", {"Date[Year]": [y]})
        assert (got or 0.0) == pytest.approx(want), f"{y}: revenue by ship date should be {want:,.2f}, got {got}"


def test_the_order_date_measure_is_unchanged():
    m, t = model()
    f = flat_of(t)
    for y in (2023, 2024):
        assert m.evaluate("Revenue", {"Date[Year]": [y]}) == pytest.approx(f.loc[f["Year"] == y, "Revenue"].sum()), "[Revenue] still follows the order date."
    assert m.evaluate("Revenue", {"Date[Year]": [2025]}) is None, "no order was placed in 2025, so [Revenue] is blank there."


def test_the_two_measures_differ_but_add_up():
    m, t = model()
    assert m.evaluate("Revenue by ship date", {"Date[Year]": [2025]}) is not None, "orders placed in late December 2024 ship in 2025."
    total = lambda name: sum((m.evaluate(name, {"Date[Year]": [y]}) or 0.0) for y in (2023, 2024, 2025))
    assert total("Revenue") == pytest.approx(total("Revenue by ship date")), "over all years both add up to the same total."
    assert "USERELATIONSHIP" in ship_date_measure().upper(), "use USERELATIONSHIP."
