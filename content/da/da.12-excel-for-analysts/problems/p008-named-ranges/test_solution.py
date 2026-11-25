import numpy as np
import pandas as pd
import pytest

from openpyxl import Workbook

from conftest import Book
from solution import set_names

ROWS = [("N", "Kitchen", 100.0), ("S", "Living", 250.5), ("N", "Living", 80.0), ("E", "Kitchen", 40.25), ("S", "Kitchen", 10.0)]


def make(rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    ws.append(["id", "region", "category", "revenue"])
    for i, (reg, cat, rev) in enumerate(rows, 1):
        ws.append([f"O{i}", reg, cat, rev])
    return wb


def total(wb, formula):
    wb["Orders"]["H1"] = formula
    return Book(wb).value("Orders", "H1")


def test_names_cover_the_data_rows():
    wb = make(ROWS)
    set_names(wb, len(ROWS))
    assert wb.defined_names["Rev"].attr_text == "Orders!$D$2:$D$6", f"Rev should refer to Orders!$D$2:$D$6, got {wb.defined_names['Rev'].attr_text!r}"
    assert wb.defined_names["Region"].attr_text == "Orders!$B$2:$B$6" and wb.defined_names["Cat"].attr_text == "Orders!$C$2:$C$6"


def test_formulas_with_names_match_the_data():
    wb = make(ROWS)
    set_names(wb, len(ROWS))
    assert total(wb, "=SUM(Rev)") == pytest.approx(sum(r[2] for r in ROWS))
    assert total(wb, '=SUMIFS(Rev,Region,"N",Cat,"Living")') == pytest.approx(80.0), "named ranges work inside SUMIFS."


def test_calling_again_after_the_data_grew_replaces_the_names():
    wb = make(ROWS)
    set_names(wb, len(ROWS))
    more = [("W", "Outdoor", 500.0), ("N", "Outdoor", 5.0), ("N", "Kitchen", 1.0)]
    for i, (reg, cat, rev) in enumerate(more, 6):
        wb["Orders"].append([f"O{i}", reg, cat, rev])
    set_names(wb, len(ROWS) + len(more))
    assert wb.defined_names["Rev"].attr_text == "Orders!$D$2:$D$9", "after appending 3 rows the name must end at row 9 (a stale name leaves the new rows out)."
    assert total(wb, "=SUM(Rev)") == pytest.approx(sum(r[2] for r in ROWS + more))
    assert len([n for n in wb.defined_names if n == "Rev"]) == 1, "replace the name; do not add a second one."


def test_other_sheet_name():
    wb = make(ROWS)
    wb["Orders"].title = "Data"
    set_names(wb, 5, sheet="Data")
    assert wb.defined_names["Rev"].attr_text.startswith("Data!"), "the sheet argument is used."
