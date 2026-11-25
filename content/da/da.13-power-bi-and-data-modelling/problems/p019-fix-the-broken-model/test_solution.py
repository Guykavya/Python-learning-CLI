import numpy as np
import pandas as pd
import pytest

from conftest import Model, flat_of, make_mini
from solution import build_model

T = make_mini(seed=3, n_orders=140)
F = flat_of(T)


def check_relationships_frame(m):
    rows = []
    for r in m.rels:
        many, one = m.t[r.many][r.mcol], m.t[r.one][r.ocol]
        rows.append((r, bool(one.is_unique), int(many.isna().sum()), int((~many.dropna().isin(one)).sum())))
    return rows


def lint_model(m):
    issues = []
    for r, unique, blank, orphan in check_relationships_frame(m):
        name = f"{r.many}[{r.mcol}] -> {r.one}[{r.ocol}]"
        if not unique:
            issues.append(f"{name}: the one side is not unique")
        if blank:
            issues.append(f"{name}: {blank} blank keys")
        if orphan:
            issues.append(f"{name}: {orphan} orphan rows")
        if r.both:
            issues.append(f"{name}: bidirectional")
    d = m.t["Date"]["Date"].sort_values()
    if not (d.diff().dropna() == pd.Timedelta(days=1)).all():
        issues.append("the date table has gaps")
    related = {r.many for r in m.rels} | {r.one for r in m.rels}
    issues += [f"table {t} has no relationship" for t in m.t if t not in related]
    return issues


def reachability(m, measures, dims):
    bad = []
    for meas in measures:
        for table, col in dims:
            members = sorted(m.t[table][col].dropna().unique().tolist())[:6]
            vals = [m.evaluate(meas, {f"{table}[{col}]": [v]}) for v in members]
            vals = [v for v in vals if v is not None]
            if len(vals) > 1 and all(abs(v - vals[0]) < 1e-9 for v in vals):
                bad.append((meas, f"{table}[{col}]"))
    return bad


def expected(year, cat, region):
    d = F
    if year is not None:
        d = d[d["Year"] == year]
    if cat is not None:
        d = d[d["Category"] == cat]
    if region is not None:
        d = d[d["StoreRegion"] == region]
    if len(d) == 0:
        return {k: None for k in ("Revenue", "Cost", "Margin", "Margin %", "Orders", "Customers", "Quantity")}
    rev, cost = d["Revenue"].sum(), d["Cost"].sum()
    return {"Revenue": rev, "Cost": cost, "Margin": rev - cost, "Margin %": (rev - cost) / rev, "Orders": d["OrderID"].nunique(),
            "Customers": d["CustomerKey"].nunique(), "Quantity": d["Quantity"].sum()}


def test_values_equal_pandas_on_a_grid_of_contexts():
    m = build_model(Model, T)
    bad = []
    for y in (None, 2024):
        for c in (None, "Kitchen", "Outdoor"):
            for r in (None, "North", "Online"):
                flt = {k: [v] for k, v in (("Date[Year]", y), ("Product[Category]", c), ("Store[Region]", r)) if v is not None}
                for meas, want in expected(y, c, r).items():
                    got = m.evaluate(meas, flt)
                    ok = (got is None and want is None) or (got is not None and want is not None and abs(got - want) <= 1e-6 * max(1.0, abs(want)))
                    if not ok:
                        bad.append((meas, flt, got, want))
    assert bad == [], f"{len(bad)} of the comparisons fail. First: {bad[:2]}. (Check the relationships, an ALL left in a measure, and the discount in Revenue.)"


def test_every_measure_responds_to_every_dimension_it_can_reach():
    m = build_model(Model, T)
    dims = [("Date", "Year"), ("Product", "Category"), ("Customer", "Segment"), ("Store", "Region")]
    stuck = reachability(m, ["Revenue", "Cost", "Quantity", "Orders", "Customers"], dims)
    assert stuck == [], f"these measures ignore a slicer: {stuck}"
    stuck_f = reachability(m, ["Freight"], [("Date", "Year"), ("Customer", "Segment"), ("Store", "Region")])
    assert stuck_f == [], f"freight must respond to date, customer and store: {stuck_f}"


def test_structure_is_clean_and_names_are_kept():
    m = build_model(Model, T)
    assert lint_model(m) == [], f"structural problems: {lint_model(m)}"
    assert set(m.measures) >= {"Revenue", "Quantity", "Orders", "Customers", "Cost", "Margin", "Margin %", "Freight"}, "keep the names of the measures."
