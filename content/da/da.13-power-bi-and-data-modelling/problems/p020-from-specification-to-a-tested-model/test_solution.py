import numpy as np
import pandas as pd
import pytest

import json

from conftest import DaxError, Model, flat_of, make_mini
from solution import check_report_spec, model_from_project

T = make_mini(seed=3, n_orders=120)
F = flat_of(T)

SPEC = {
    "tables": {"Date": {"file": "DimDate.parquet"}, "Product": {"file": "DimProduct.csv"}, "Store": {"file": "DimStore.csv"}, "Sales": {"file": "FactSales.parquet"}},
    "relationships": [
        {"from": "Sales[OrderDateKey]", "to": "Date[DateKey]", "direction": "single", "active": True},
        {"from": "Sales[ShipDateKey]", "to": "Date[DateKey]", "direction": "single", "active": False},
        {"from": "Sales[ProductKey]", "to": "Product[ProductKey]", "direction": "single", "active": True},
        {"from": "Sales[StoreKey]", "to": "Store[StoreKey]", "direction": "single", "active": True},
    ],
    "measures": [
        {"name": "Revenue", "dax": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))"},
        {"name": "Quantity", "dax": "SUM(Sales[Quantity])"},
        {"name": "Revenue per unit", "dax": "DIVIDE([Revenue], [Quantity])"},
    ],
}
REPORT = {
    "Overview": {"slicers": ["Date[Year]", "Store[Region]"], "visuals": [
        {"type": "card", "measure": "Revenue"}, {"type": "bar", "axis": "Product[Category]", "measures": ["Revenue", "Revenue per unit"]}]},
    "Detail": {"slicers": [], "visuals": [{"type": "table", "rows": "Store[Store]", "measures": ["Quantity"]}]},
}


def write_project(folder, spec=SPEC, product=None):
    folder.mkdir(exist_ok=True)
    T["Date"].to_parquet(folder / "DimDate.parquet", index=False)
    T["Sales"].to_parquet(folder / "FactSales.parquet", index=False)
    (T["Product"] if product is None else product).to_csv(folder / "DimProduct.csv", index=False)
    T["Store"].to_csv(folder / "DimStore.csv", index=False)
    (folder / "model_spec.json").write_text(json.dumps(spec), encoding="utf-8")
    return folder


def test_the_model_is_rebuilt_from_the_files(tmp_path):
    m, spec = model_from_project(write_project(tmp_path / "p"), Model)
    assert isinstance(m, Model) and spec["measures"][0]["name"] == "Revenue" and set(m.t) == {"Date", "Product", "Store", "Sales"}, f"tables {set(m.t)}"
    assert len(m.rels) == 4 and [r.active for r in m.rels] == [True, False, True, True], "four relationships, the ship date one inactive."
    assert m.t["Date"]["Date"].dtype.kind == "M", "Parquet keeps the dates as dates."


def test_the_measures_equal_pandas(tmp_path):
    m, _ = model_from_project(write_project(tmp_path / "p"), Model)
    assert m.evaluate("Revenue") == pytest.approx(F["Revenue"].sum())
    assert m.evaluate("Revenue", {"Date[Year]": [2024], "Store[Region]": ["North"]}) == pytest.approx(F[(F["Year"] == 2024) & (F["StoreRegion"] == "North")]["Revenue"].sum())
    assert m.evaluate("Revenue per unit", {"Product[Category]": ["Kitchen"]}) == pytest.approx(F[F["Category"] == "Kitchen"]["Revenue"].sum() / F[F["Category"] == "Kitchen"]["Quantity"].sum()), "a measure may use an earlier one."


def test_a_duplicate_key_on_the_one_side_fails_with_a_clear_message(tmp_path):
    dup = T["Product"].copy()
    dup.loc[1, "ProductKey"] = dup.loc[0, "ProductKey"]
    with pytest.raises(ValueError, match=r"relationship Sales\[ProductKey\] -> Product\[ProductKey\]"):
        model_from_project(write_project(tmp_path / "bad", product=dup), Model)


def test_both_direction_is_honoured(tmp_path):
    spec = json.loads(json.dumps(SPEC))
    spec["relationships"][3]["direction"] = "both"
    m, _ = model_from_project(write_project(tmp_path / "b", spec), Model)
    assert [r.both for r in m.rels] == [False, False, False, True]


def test_a_good_report_spec_has_no_problems(tmp_path):
    m, spec = model_from_project(write_project(tmp_path / "p"), Model)
    assert check_report_spec(REPORT, m, spec) == [], f"got {check_report_spec(REPORT, m, spec)}"


def test_a_report_with_mistakes(tmp_path):
    m, spec = model_from_project(write_project(tmp_path / "p"), Model)
    report = {"Overview": {"slicers": ["Date[Year]", "Store[Regoin]"], "visuals": [
                 {"type": "card", "measure": "Revnue"}, {"type": "bar", "axis": "Product[Colour]", "measures": ["Revenue", "Margin"]}]},
              "Detail": {"slicers": ["Customer[Segment]"], "visuals": [{"type": "table", "rows": "Store[Store]", "columns": "Date[Nope]", "measures": ["Quantity"]}]}}
    assert check_report_spec(report, m, spec) == [
        "Overview: slicer field Store[Regoin] does not exist",
        "Overview: measure [Revnue] does not exist",
        "Overview: measure [Margin] does not exist",
        "Overview: field Product[Colour] does not exist",
        "Detail: slicer field Customer[Segment] does not exist",
        "Detail: field Date[Nope] does not exist",
    ], f"got {check_report_spec(report, m, spec)}"
