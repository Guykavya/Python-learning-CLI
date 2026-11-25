import numpy as np
import pandas as pd
import pytest

from conftest import DaxError, Model, build_model, make_mini
from solution import check_relationships


def test_a_healthy_model():
    chk = check_relationships(build_model(make_mini()))
    assert list(chk.columns) == ["relationship", "one side unique", "blank keys", "orphan rows", "direction", "active"], f"columns, got {list(chk.columns)}"
    assert len(chk) == 8 and chk["one side unique"].all() and (chk["blank keys"] == 0).all() and (chk["orphan rows"] == 0).all(), "eight relationships, all healthy."
    assert (chk["direction"] == "single").all() and chk["active"].tolist() == [True, False, True, True, True, True, True, True], "one inactive relationship (ship date)."
    assert chk.loc[0, "relationship"] == "Sales[OrderDateKey] -> Date[DateKey]", f"relationship text, got {chk.loc[0, 'relationship']!r}"


def test_orphan_blank_and_bidirectional_are_reported():
    t = make_mini()
    m = build_model(t, both=("Sales-Product",))
    sales = m.t["Sales"].copy()
    sales.loc[0, "ProductKey"] = 99
    sales.loc[1, "ProductKey"] = None
    sales.loc[2, "StoreKey"] = 77
    m.t["Sales"] = sales
    chk = check_relationships(m).set_index("relationship")
    p = chk.loc["Sales[ProductKey] -> Product[ProductKey]"]
    assert p["orphan rows"] == 1 and p["blank keys"] == 1 and p["direction"] == "both", f"one orphan (99), one blank (None), bidirectional; got {p.to_dict()}"
    s = chk.loc["Sales[StoreKey] -> Store[StoreKey]"]
    assert s["orphan rows"] == 1 and s["blank keys"] == 0 and s["direction"] == "single"
    assert type(p["orphan rows"]).__name__.startswith("int"), "counts are ints."


def test_a_duplicate_on_the_one_side():
    m = build_model(make_mini())
    prod = m.t["Product"].copy()
    prod.loc[1, "ProductKey"] = prod.loc[0, "ProductKey"]
    m.t["Product"] = prod
    chk = check_relationships(m)
    row = chk[chk["relationship"] == "Sales[ProductKey] -> Product[ProductKey]"].iloc[0]
    assert not bool(row["one side unique"]), "the one side has a duplicate key."
    assert chk["one side unique"].sum() == len(chk) - 1, "only that relationship is flagged."
