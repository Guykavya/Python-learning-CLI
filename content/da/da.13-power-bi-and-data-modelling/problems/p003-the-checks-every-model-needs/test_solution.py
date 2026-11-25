import numpy as np
import pandas as pd
import pytest

from solution import check_star

DIMS = {"DimProduct": pd.DataFrame({"ProductKey": [1, 2, 3], "Product": ["a", "b", "c"]}),
        "DimStore": pd.DataFrame({"StoreKey": [1, 2], "Store": ["x", "y"]})}
FACTS = {"FactSales": pd.DataFrame({"ProductKey": [1, 2, 3, 1], "StoreKey": [1, 1, 2, 2], "Amount": [5, 6, 7, 8]})}
KEYS = [("FactSales", "ProductKey", "DimProduct", "ProductKey"), ("FactSales", "StoreKey", "DimStore", "StoreKey")]


def test_a_good_star():
    assert check_star(FACTS, DIMS, KEYS) == [], "no problems in a clean model."


def test_three_planted_faults():
    dims = {"DimProduct": pd.DataFrame({"ProductKey": [1, 2, 2], "Product": ["a", "b", "c"]}), "DimStore": DIMS["DimStore"]}
    facts = {"FactSales": pd.DataFrame({"ProductKey": [1, 2, 99, None], "StoreKey": [1, 1, 2, 7], "Amount": [5, 6, 7, 8]})}
    got = check_star(facts, dims, KEYS)
    assert got == ["DimProduct[ProductKey] has duplicate keys", "FactSales[ProductKey] has 1 blank keys",
                   "FactSales[ProductKey] has 1 orphan rows (not in DimProduct[ProductKey])", "FactSales[StoreKey] has 1 orphan rows (not in DimStore[StoreKey])"], f"got {got}"


def test_blank_dimension_key_and_order_of_messages():
    dims = {"DimStore": pd.DataFrame({"StoreKey": [1, None], "Store": ["x", "y"]}), "DimProduct": DIMS["DimProduct"]}
    got = check_star(FACTS, dims, KEYS)
    assert got[0] == "DimStore[StoreKey] has blank keys", f"dimension problems first, in dict order; got {got}"
    assert len(got) == 1 + 1, "StoreKey 2 is not in the damaged dimension: one orphan row too."
    assert got[1].startswith("FactSales[StoreKey] has 2 orphan"), got[1]
