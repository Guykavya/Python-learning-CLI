import numpy as np
import pandas as pd
import pytest

from conftest import REVENUE, build_model, flat_of, make_mini
from solution import add_budget

T = make_mini(seed=3, n_orders=200)
F = flat_of(T)


def make_budget():
    mon = F.assign(MonthStart=pd.to_datetime(F["Year"].astype(str) + "-" + F["Month"].astype(str).str.zfill(2) + "-01")).groupby(["MonthStart", "Category"])["Revenue"].sum().reset_index()
    rng = np.random.default_rng(8)
    mon["BudgetRevenue"] = (mon["Revenue"] * rng.uniform(0.9, 1.15, len(mon))).round(0)
    return mon[["MonthStart", "Category", "BudgetRevenue"]], mon


def model():
    budget, mon = make_budget()
    m = build_model(T)
    m.measure("Revenue", REVENUE)
    add_budget(m, budget)
    return m, budget, mon


def test_budget_and_attainment_by_category_and_month():
    m, budget, mon = model()
    q = m.query(["DimCategory[Category]", "DimMonth[YearMonth]"], ["Revenue", "Budget", "Attainment %"], filters={"DimMonth[Year]": [2024]})
    mon24 = mon[mon["MonthStart"].dt.year == 2024].assign(YearMonth=lambda t: t["MonthStart"].dt.strftime("%Y-%m"))
    got = q.merge(mon24, left_on=["DimCategory[Category]", "DimMonth[YearMonth]"], right_on=["Category", "YearMonth"])
    assert len(got) == len(mon24) and len(got) > 10, "one row per category and month of 2024."
    assert np.allclose(got["Budget"], got["BudgetRevenue"]) and np.allclose(got["Revenue_x"], got["Revenue_y"]), "budget and revenue match pandas in every cell."
    assert np.allclose(got["Attainment %"], got["Revenue_y"] / got["BudgetRevenue"]), "attainment = revenue / budget."


def test_budget_is_blank_at_product_level():
    m, _, _ = model()
    q = m.query(["Product[Product]"], ["Revenue", "Budget"])
    assert len(q) > 0 and q["Budget"].isna().all(), "the budget does not exist per product: blank, not the category budget repeated."


def test_totals_and_relationships():
    m, budget, _ = model()
    assert m.evaluate("Budget") == pytest.approx(budget["BudgetRevenue"].sum()), "the grand total of the budget is the sum of the budget table."
    names = {(r.many, r.mcol, r.one, r.ocol) for r in m.rels}
    for rel in (("Date", "MonthStart", "DimMonth", "MonthStart"), ("Product", "Category", "DimCategory", "Category"), ("Budget", "MonthStart", "DimMonth", "MonthStart"), ("Budget", "Category", "DimCategory", "Category")):
        assert rel in names, f"missing relationship {rel}"
    assert m.evaluate("Budget", {"Product[Category]": ["Kitchen"]}) == pytest.approx(budget["BudgetRevenue"].sum()), "a filter on the product table does not reach the budget (one-way): the budget is not trimmed by it."
