import numpy as np
import pandas as pd
import pytest

from conftest import build_model, flat_of, make_mini
from solution import MEASURES

T = make_mini(seed=3, n_orders=160)
F = flat_of(T)


def model():
    m = build_model(T)
    for name, expr in MEASURES.items():
        m.measure(name, expr)
    return m


def pandas_vals(d):
    if len(d) == 0:
        return {"Cost": None, "Margin": None, "Margin %": None}
    rev, cost = d["Revenue"].sum(), d["Cost"].sum()
    return {"Cost": cost, "Margin": rev - cost, "Margin %": (rev - cost) / rev}


def test_every_level_equals_pandas():
    m = model()
    bad = []
    for y in (None, 2024):
        for c in (None, "Kitchen", "Outdoor"):
            for r in (None, "North", "Online"):
                flt, d = {}, F
                if y is not None:
                    flt["Date[Year]"], d = [y], d[d["Year"] == y]
                if c is not None:
                    flt["Product[Category]"], d = [c], d[d["Category"] == c]
                if r is not None:
                    flt["Store[Region]"], d = [r], d[d["StoreRegion"] == r]
                for name, want in pandas_vals(d).items():
                    got = m.evaluate(name, flt)
                    ok = (got is None and want is None) or (got is not None and want is not None and abs(got - want) <= 1e-9 * max(1.0, abs(want)))
                    if not ok:
                        bad.append((name, flt, got, want))
    assert bad == [], f"{len(bad)} contexts differ from pandas; first: {bad[:2]}"


def test_the_wrong_way_gives_another_number():
    m = model()
    wrong = (1 - F["Cost"] / F["Revenue"]).mean()
    right = m.evaluate("Margin %")
    assert abs(wrong - right) > 0.002, "(data check) the average of the per-line margin percentages differs from the ratio of sums."
    assert right == pytest.approx((F["Revenue"].sum() - F["Cost"].sum()) / F["Revenue"].sum()), "the right margin % is sum(margin) / sum(revenue)."


def test_margin_is_additive_but_the_percentage_is_not():
    m = model()
    q = m.query(["Product[Category]"], ["Margin", "Margin %"])
    assert q["Margin"].sum() == pytest.approx(m.evaluate("Margin")), "margin amounts add up across categories."
    assert q["Margin %"].sum() != pytest.approx(m.evaluate("Margin %")), "the percentages of the categories do not add up to the total percentage."
