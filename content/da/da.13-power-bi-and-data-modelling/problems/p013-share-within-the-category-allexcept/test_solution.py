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


def test_shares_within_each_category_add_up_to_one():
    q = model().query(["Product[Category]", "Product[Product]"], ["% of category"])
    assert np.allclose(q.groupby("Product[Category]")["% of category"].sum(), 1.0), "within each category the product shares add up to 1."


def test_equals_pandas_transform_in_a_context():
    m = model()
    for flt, d in (({}, F), ({"Date[Year]": [2024]}, F[F["Year"] == 2024]), ({"Store[Region]": ["North"]}, F[F["StoreRegion"] == "North"])):
        q = m.query(["Product[Category]", "Product[Product]"], ["% of category"], filters=flt)
        g = d.groupby(["Category", "Product"])["Revenue"].sum().reset_index()
        g["want"] = g["Revenue"] / g.groupby("Category")["Revenue"].transform("sum")
        got = q.merge(g, left_on=["Product[Category]", "Product[Product]"], right_on=["Category", "Product"])
        assert len(got) == len(g) and np.allclose(got["% of category"], got["want"]), f"filters {flt}: shares must equal revenue / category revenue in the same context (year and region stay)."


def test_a_category_row_is_100_percent_and_blank_when_empty():
    m = model()
    q = m.query(["Product[Category]"], ["% of category"])
    assert np.allclose(q["% of category"], 1.0), "at category level the share of the category is 1."
    assert m.evaluate("% of category", {"Date[Year]": [2025]}) is None, "no sales: blank."
