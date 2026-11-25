import numpy as np
import pandas as pd
import pytest

from conftest import build_model, flat_of, make_mini
from solution import MEASURES

T = make_mini(seed=3, n_orders=140)
F = flat_of(T)


def pandas_values(year, cat, region):
    d = F
    if year is not None:
        d = d[d["Year"] == year]
    if cat is not None:
        d = d[d["Category"] == cat]
    if region is not None:
        d = d[d["StoreRegion"] == region]
    if len(d) == 0:
        return {"Revenue": None, "Orders": None, "Average order value": None}
    rev, n = d["Revenue"].sum(), d["OrderID"].nunique()
    return {"Revenue": rev, "Orders": n, "Average order value": rev / n}


def model():
    m = build_model(T)
    for name, expr in MEASURES.items():
        m.measure(name, expr)
    return m


def test_the_measures_are_defined_in_order():
    assert list(MEASURES) == ["Revenue", "Orders", "Average order value"], f"three measures in this order; got {list(MEASURES)}"


def test_grid_of_contexts_against_pandas():
    m = model()
    failures = []
    for y in (None, 2024):
        for c in (None, "Kitchen", "Outdoor"):
            for r in (None, "North", "Online"):
                flt = {k: [v] for k, v in (("Date[Year]", y), ("Product[Category]", c), ("Store[Region]", r)) if v is not None}
                for name, want in pandas_values(y, c, r).items():
                    got = m.evaluate(name, flt)
                    ok = (got is None and want is None) or (got is not None and want is not None and abs(got - want) <= 1e-9 * max(1.0, abs(want)))
                    if not ok:
                        failures.append((name, flt, got, want))
    assert failures == [], f"{len(failures)} contexts differ from pandas, first: {failures[:2]} (remember: no sales means BLANK; Orders counts distinct orders)"


def test_blank_not_zero():
    m = model()
    flt = {"Date[Year]": [2025]}
    assert all(m.evaluate(n, flt) is None for n in MEASURES), "in 2025 there are no sales: every measure is BLANK (None), not 0."
