import numpy as np
import pandas as pd
import pytest

from solution import build_star

FLAT = pd.DataFrame({
    "order_id": ["O1", "O1", "O2", "O3", "O3"], "line_no": [1, 2, 1, 1, 2],
    "order_date": pd.to_datetime(["2024-01-05", "2024-01-05", "2024-01-06", "2024-02-01", "2024-02-01"]),
    "customer": ["Zed", "Zed", "Amy", "Amy", "Amy"], "segment": ["Consumer", "Consumer", "Corporate", "Corporate", "Corporate"], "city": ["Pune", "Pune", "Delhi", "Delhi", "Delhi"],
    "product": ["Product B", "Product A", "Product B", "Product B", "Product C"], "category": ["Kitchen", "Living", "Kitchen", "Kitchen", "Outdoor"],
    "store": ["S2", "S2", "S1", "S1", "S2"], "quantity": [2, 1, 3, 1, 4], "unit_price": [10.0, 20.0, 10.5, 9.0, 5.0], "discount": [0.0, 0.1, 0.0, 0.05, 0.2]})


def test_dimensions_are_one_row_per_natural_key_with_sorted_integer_keys():
    fact, dims = build_star(FLAT)
    assert set(dims) == {"DimProduct", "DimCustomer", "DimStore"}, f"three dimensions, got {set(dims)}"
    p = dims["DimProduct"]
    assert list(p.columns) == ["ProductKey", "product", "category"] and p["product"].tolist() == ["Product A", "Product B", "Product C"] and p["ProductKey"].tolist() == [1, 2, 3], f"keys follow the sorted natural key; got {p.to_dict('list')}"
    c = dims["DimCustomer"]
    assert list(c.columns) == ["CustomerKey", "customer", "segment", "city"] and c["customer"].tolist() == ["Amy", "Zed"] and c["CustomerKey"].tolist() == [1, 2]
    assert dims["DimStore"]["store"].tolist() == ["S1", "S2"] and list(dims["DimStore"].columns) == ["StoreKey", "store"]
    assert all(d.iloc[:, 0].is_unique for d in dims.values()), "dimension keys are unique."


def test_fact_has_the_same_rows_and_integer_keys():
    fact, _ = build_star(FLAT)
    assert list(fact.columns) == ["order_id", "line_no", "order_date", "ProductKey", "CustomerKey", "StoreKey", "quantity", "unit_price", "discount"], f"columns, got {list(fact.columns)}"
    assert len(fact) == len(FLAT) and fact["order_id"].tolist() == FLAT["order_id"].tolist(), "one fact row per flat row, in the same order."
    assert fact["ProductKey"].tolist() == [2, 1, 2, 2, 3] and fact["CustomerKey"].tolist() == [2, 2, 1, 1, 1] and fact["StoreKey"].tolist() == [2, 2, 1, 1, 2]
    assert fact["ProductKey"].dtype.kind == "i", "integer keys."


def test_joining_back_reproduces_the_revenue():
    fact, dims = build_star(FLAT)
    back = fact.merge(dims["DimProduct"], on="ProductKey", validate="m:1").merge(dims["DimCustomer"], on="CustomerKey", validate="m:1").merge(dims["DimStore"], on="StoreKey", validate="m:1")
    rev = lambda d: (d["quantity"] * d["unit_price"] * (1 - d["discount"])).sum()
    assert len(back) == len(FLAT) and rev(back) == pytest.approx(rev(FLAT)), "revenue after joining back equals the revenue of the flat table."
    assert back["category"].tolist() == FLAT["category"].tolist() and back["city"].tolist() == FLAT["city"].tolist()


def test_conflicting_attributes():
    bad = FLAT.copy()
    bad.loc[0, "category"] = "Living"
    with pytest.raises(ValueError, match="conflicting attributes for product Product B"):
        build_star(bad)
    bad2 = FLAT.copy()
    bad2.loc[4, "city"] = "Mumbai"
    with pytest.raises(ValueError, match="conflicting attributes for customer Amy"):
        build_star(bad2)
