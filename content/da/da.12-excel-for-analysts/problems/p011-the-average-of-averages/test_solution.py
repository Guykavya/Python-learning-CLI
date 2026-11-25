import numpy as np
import pandas as pd
import pytest

from openpyxl import Workbook
from openpyxl.workbook.defined_name import DefinedName

from conftest import Book
from solution import add_price_metrics

ORDERS = pd.DataFrame({"region": ["North", "North", "North", "South", "South"], "units": [1, 9, 4, 5, 5],
                       "price": [10.0, 20.0, 12.5, 8.0, 9.0], "discount": [0.0, 0.0, 0.1, 0.0, 0.2]})


def make():
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    ws.append(["region", "units", "price", "discount", "revenue"])
    for i, r in enumerate(ORDERS.itertuples(index=False), 2):
        ws.append(list(r) + [f"=B{i}*C{i}*(1-D{i})"])
    n = len(ORDERS) + 1
    for name, col in (("Region", "A"), ("Units", "B"), ("Price", "C"), ("Rev", "E")):
        wb.defined_names[name] = DefinedName(name, attr_text=f"Orders!${col}$2:${col}${n}")
    return wb


def truth(region):
    d = ORDERS[ORDERS["region"] == region].assign(rev=lambda t: t["units"] * t["price"] * (1 - t["discount"]))
    return d["price"].mean(), d["rev"].sum() / d["units"].sum()


@pytest.mark.parametrize("region", ["North", "South"])
def test_both_metrics_match_pandas(region):
    wb = make()
    add_price_metrics(wb, region)
    book = Book(wb)
    simple, weighted = truth(region)
    assert book.value("Summary", "B1") == pytest.approx(simple), f"{region}: the simple average of the line prices is {simple:.4f}"
    assert book.value("Summary", "B2") == pytest.approx(weighted), f"{region}: revenue per unit is {weighted:.4f}"


def test_the_two_numbers_differ_and_labels():
    wb = make()
    ws = add_price_metrics(wb, "North")
    assert ws["A1"].value == "Average line price" and ws["A2"].value == "Revenue per unit", "labels in A1 and A2."
    book = Book(wb)
    assert abs(book.value("Summary", "B1") - book.value("Summary", "B2")) > 0.5, "the two answers are different numbers on this data: the average of averages is not revenue per unit."


def test_formulas_use_the_right_functions():
    wb = make()
    ws = add_price_metrics(wb, "North")
    assert "AVERAGEIFS" in ws["B1"].value.upper() and ws["B2"].value.upper().count("SUMIFS") == 2, "B1 is an AVERAGEIFS; B2 is SUMIFS / SUMIFS."
