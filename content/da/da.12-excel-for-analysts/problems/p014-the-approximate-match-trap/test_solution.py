import numpy as np
import pandas as pd
import pytest

from openpyxl import Workbook

from conftest import Book
from solution import add_prices

PRODUCTS = pd.DataFrame({"code": ["P07", "P02", "P09", "P01", "P05", "P03"], "price": [70.0, 20.0, 90.0, 10.0, 50.0, 30.0]})
ORDERS = pd.DataFrame({"order_id": [f"O{i}" for i in range(1, 9)], "code": ["P01", "P05", "P09", "P03", "P07", "P04", "P02", "P05"]})


def make():
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    ws.append(["order_id", "code"])
    for r in ORDERS.itertuples(index=False):
        ws.append(list(r))
    wp = wb.create_sheet("Products")
    wp.append(["code", "price"])
    for r in PRODUCTS.itertuples(index=False):
        wp.append(list(r))
    return wb


def test_every_price_is_the_exact_match():
    wb = make()
    add_prices(wb)
    book = Book(wb)
    merged = ORDERS.merge(PRODUCTS, on="code", how="left")["price"].tolist()
    got = [book.value("Orders", f"C{r}") for r in range(2, len(ORDERS) + 2)]
    for i, (g, m) in enumerate(zip(got, merged)):
        if m != m:
            assert g == "not found", f"row {i + 2}: P04 is not in Products: expected 'not found', got {g!r}"
        else:
            assert g == pytest.approx(m), f"row {i + 2} ({ORDERS['code'][i]}): expected {m}, got {g!r}. Approximate match on unsorted codes returns a neighbour's price: ask for an EXACT match."


def test_the_formula_asks_for_an_exact_match():
    wb = make()
    add_prices(wb)
    f = wb["Orders"]["C2"].value.replace(" ", "").upper()
    assert "XLOOKUP" in f or "FALSE" in f or ",0)" in f, f"use XLOOKUP, or VLOOKUP with FALSE (or 0) as the fourth argument; got {f!r}"
    assert "$A$2" in f, "keep the table reference absolute."


def test_missing_code_is_not_a_neighbours_price():
    wb = make()
    add_prices(wb)
    assert Book(wb).value("Orders", "C7") == "not found", "P04 sits between P03 and P05 in the sorted list: an approximate match would return a price."
