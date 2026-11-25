import numpy as np
import pandas as pd
import pytest

from conftest import build_model, flat_of, make_mini
from solution import MEASURES

T = make_mini(seed=3, n_orders=140)
F = flat_of(T)


def rev(year=None, cat=None, region=None):
    d = F
    if year is not None:
        d = d[d["Year"] == year]
    if cat is not None:
        d = d[d["Category"] == cat]
    if region is not None:
        d = d[d["StoreRegion"] == region]
    return None if len(d) == 0 else float(d["Revenue"].sum())


def model():
    m = build_model(T)
    for name, expr in MEASURES.items():
        m.measure(name, expr)
    return m


def close(got, want):
    return (got is None and want is None) or (got is not None and want is not None and abs(got - want) <= 1e-9 * max(1.0, abs(want)))


def test_kitchen_revenue_replaces_the_category_filter():
    m = model()
    for y in (None, 2024):
        for c in (None, "Kitchen", "Outdoor"):
            for r in (None, "North", "Online"):
                flt = {k: [v] for k, v in (("Date[Year]", y), ("Product[Category]", c), ("Store[Region]", r)) if v is not None}
                got, want = m.evaluate("Kitchen revenue", flt), rev(y, "Kitchen", r)
                assert close(got, want), f"year={y}, category={c}, region={r}: Kitchen revenue should be {want}, got {got}. A filter on a column REPLACES the visual's filter on that column; year and region are kept."


def test_percent_of_all_revenue():
    m = model()
    for y in (None, 2024):
        for c in (None, "Kitchen", "Outdoor"):
            for r in (None, "North", "Online"):
                flt = {k: [v] for k, v in (("Date[Year]", y), ("Product[Category]", c), ("Store[Region]", r)) if v is not None}
                num, den = rev(y, c, r), rev(y, None, r)
                want = None if num is None or not den else num / den
                got = m.evaluate("% of all revenue", flt)
                assert close(got, want), f"year={y}, category={c}, region={r}: expected {want}, got {got} (ALL(Product) removes the product filters only)."


def test_shares_add_up_and_blank_when_empty():
    m = model()
    q = m.query(["Product[Category]"], ["% of all revenue"], filters={"Date[Year]": [2024]})
    assert q["% of all revenue"].sum() == pytest.approx(1.0), "the shares of the categories add up to 1."
    assert m.evaluate("% of all revenue", {"Date[Year]": [2025]}) is None, "no sales: blank."
