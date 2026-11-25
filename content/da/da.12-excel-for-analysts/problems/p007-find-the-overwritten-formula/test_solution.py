import numpy as np
import pandas as pd
import pytest

from openpyxl import Workbook

from solution import column_consistency


def make(n=8):
    ws = Workbook().active
    ws.append(["units", "price", "revenue", "cost"])
    for r in range(2, n + 2):
        ws.append([r, 2.5, f"=A{r}*B{r}*(1-0.1)", f"=A{r}*1.2"])
    return ws


def test_clean_columns():
    ws = make()
    assert column_consistency(ws, "C") == [] and column_consistency(ws, "D") == [], "every row is the first row's formula copied down: no problems."


def test_typed_value_and_edited_formula_are_found():
    ws = make()
    ws["C5"] = 999.99
    ws["D8"] = "=A8*1.02"
    assert column_consistency(ws, "C") == [(5, 999.99)], f"the typed number in C5 must be reported with its content, got {column_consistency(ws, 'C')}"
    assert column_consistency(ws, "D") == [(8, "=A8*1.02")], f"the edited formula in D8, got {column_consistency(ws, 'D')}"


def test_blank_cell_in_the_middle():
    ws = make()
    ws["C4"] = None
    assert column_consistency(ws, "C") == [(4, None)], "an empty cell inside a formula column is also a fault."


def test_first_row_parameter_and_errors():
    ws = make()
    assert column_consistency(ws, "C", first_row=4) == [], "with first_row = 4 the pattern is row 4 and only the rows below are compared."
    ws["C5"] = 1
    assert column_consistency(ws, "C", first_row=4) == [(5, 1)]
    with pytest.raises(ValueError, match="the first row is not a formula"):
        column_consistency(ws, "A")
