import numpy as np
import pandas as pd
import pytest

from openpyxl import Workbook

from conftest import Book
from solution import add_price_lookup

PRODUCTS = pd.DataFrame({"code": ["P03", "P01", "P05", "P02", "P04"], "price": [30.5, 10.0, 50.25, 20.0, 40.0]})
ORDERS = pd.DataFrame({"order_id": ["O1", "O2", "O3", "O4", "O5", "O6"], "code": ["P05", "P01", "P02", "P99", "p03", "P04"]})


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


@pytest.mark.parametrize("how", ["xlookup", "index_match"])
def test_prices_match_the_merge(how):
    wb = make()
    add_price_lookup(wb, how)
    assert wb["Orders"]["C1"].value == "price", "header in C1."
    book = Book(wb)
    merged = ORDERS.assign(code=ORDERS["code"].str.upper()).merge(PRODUCTS, on="code", how="left")["price"].tolist()
    got = [book.value("Orders", f"C{r}") for r in range(2, len(ORDERS) + 2)]
    for g, m in zip(got, merged):
        if m != m:
            assert g == "not found", f"a code that is not in Products must show 'not found', got {g!r}"
        else:
            assert g == pytest.approx(m), f"price of the code: expected {m}, got {g!r}"
    assert got[3] == "not found" and got[4] == pytest.approx(30.5), "P99 is missing; the lookup is case-insensitive, so 'p03' finds P03."


@pytest.mark.parametrize("how,needle", [("xlookup", "XLOOKUP"), ("index_match", "MATCH")])
def test_formula_shape(how, needle):
    wb = make()
    add_price_lookup(wb, how)
    f = wb["Orders"]["C3"].value.replace(" ", "")
    assert needle in f.upper() and "$A$2:$A$6" in f and "$B$2:$B$6" in f, f"absolute ranges over the whole Products table (rows 2 to 6), got {f!r}"
    if how == "index_match":
        assert ",0)" in f, "MATCH must be exact: the third argument is 0."


def test_bad_argument():
    with pytest.raises(ValueError, match="how must be 'xlookup' or 'index_match'"):
        add_price_lookup(make(), "vlookup")
