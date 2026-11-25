import numpy as np
import pandas as pd
import pytest

from openpyxl import Workbook

from conftest import Book
from solution import add_margin_column

LINES = [("O1", 10, 12.5, 7.0), ("O2", 3, 40.0, 25.5), ("O3", 8, 9.99, 6.0), ("O4", 1, 100.0, 80.0)]


def make(rate=0.10, rate_at="M1"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    ws.append(["id", "units", "unit_price", "unit_cost"])
    for line in LINES:
        ws.append(list(line))
    ws[rate_at] = rate
    return wb, ws


def expected(rate):
    return [u * p - u * c * (1 + rate) for _, u, p, c in LINES]


def test_values_match_pandas_style_calculation():
    wb, ws = make()
    add_margin_column(ws, len(LINES))
    assert ws["E1"].value == "margin", "the header 'margin' goes in E1."
    book = Book(wb)
    got = [book.value("Orders", f"E{r}") for r in range(2, len(LINES) + 2)]
    assert got == pytest.approx(expected(0.10)), f"margin = units * price - units * cost * (1 + rate); expected {expected(0.10)}, got {got}"


def test_every_row_uses_the_absolute_reference():
    wb, ws = make()
    add_margin_column(ws, len(LINES))
    for r in range(2, len(LINES) + 2):
        f = ws[f"E{r}"].value
        assert "$M$1" in f, f"E{r} = {f!r}: without `$`, the reference moves when the formula is filled down."
        assert f.replace(" ", "").upper() == f"=B{r}*C{r}-B{r}*D{r}*(1+$M$1)", f"E{r}: expected the shape =B{r}*C{r}-B{r}*D{r}*(1+$M$1), got {f!r}"


def test_changing_the_input_changes_every_margin():
    wb, ws = make(rate=0.25)
    add_margin_column(ws, len(LINES))
    got = [Book(wb).value("Orders", f"E{r}") for r in range(2, len(LINES) + 2)]
    assert got == pytest.approx(expected(0.25)), "the rate cell is read by every row: change it and all margins move."


def test_another_rate_cell():
    wb, ws = make(rate=0.5, rate_at="K2")
    add_margin_column(ws, len(LINES), rate_cell="$K$2")
    assert "$K$2" in ws["E4"].value
    assert Book(wb).value("Orders", "E5") == pytest.approx(expected(0.5)[3]), "the rate_cell argument is used as given."
