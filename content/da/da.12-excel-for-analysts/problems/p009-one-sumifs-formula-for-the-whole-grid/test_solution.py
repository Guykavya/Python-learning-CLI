import numpy as np
import pandas as pd
import pytest

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

from conftest import Book
from solution import add_grid

DATA = pd.DataFrame({"region": ["North", "North", "South", "East", "North", "South"],
                     "category": ["Kitchen", "Living", "Kitchen", "Living", "Kitchen", "Living"],
                     "revenue": [100.0, 50.5, 70.0, 20.0, 5.25, 8.0]})


def make():
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    ws.append(["region", "category", "revenue"])
    for r in DATA.itertuples(index=False):
        ws.append(list(r))
    n = len(DATA) + 1
    for name, col in (("Region", "A"), ("Category", "B"), ("Rev", "C")):
        wb.defined_names[name] = DefinedName(name, attr_text=f"Orders!${col}$2:${col}${n}")
    return wb


REGIONS, CATS = ["East", "North", "South", "West"], ["Kitchen", "Living", "Outdoor"]


def test_values_equal_the_pivot_and_missing_is_zero():
    wb = make()
    add_grid(wb, REGIONS, CATS, top=7)
    book = Book(wb)
    truth = DATA.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum").reindex(index=REGIONS, columns=CATS).fillna(0.0)
    for i, reg in enumerate(REGIONS):
        for j, cat in enumerate(CATS):
            got = book.value("Summary", f"{get_column_letter(2 + j)}{8 + i}")
            assert got == pytest.approx(truth.loc[reg, cat]), f"{reg}/{cat}: expected {truth.loc[reg, cat]}, got {got} (a region and category with no rows is 0)"


def test_labels_and_formula_shape():
    wb = make()
    ws = add_grid(wb, REGIONS, CATS, top=7)
    assert wb["Summary"] is ws, "return the Summary sheet."
    assert ws["A7"].value == "Region" and [ws.cell(7, c).value for c in (2, 3, 4)] == CATS, "header row: 'Region' then the categories."
    assert [ws.cell(r, 1).value for r in range(8, 12)] == REGIONS, "region labels down column A."
    assert ws["B8"].value.replace(" ", "") == "=SUMIFS(Rev,Region,$A8,Category,B$7)", f"B8 should be =SUMIFS(Rev,Region,$A8,Category,B$7), got {ws['B8'].value!r}"
    assert ws["D11"].value.replace(" ", "") == "=SUMIFS(Rev,Region,$A11,Category,D$7)", "mixed references: $A (column fixed) and D$7 (row fixed)."


def test_other_position():
    wb = make()
    ws = add_grid(wb, ["North", "South"], ["Kitchen"], top=2, left=3)
    assert ws["C2"].value == "Region" and ws["D2"].value == "Kitchen" and ws["C3"].value == "North"
    assert ws["D4"].value.replace(" ", "") == "=SUMIFS(Rev,Region,$C4,Category,D$2)", f"the label column is C here, got {ws['D4'].value!r}"
    assert Book(wb).value("Summary", "D4") == pytest.approx(70.0)


def test_existing_summary_sheet_is_reused():
    wb = make()
    wb.create_sheet("Summary")["Z1"] = "keep me"
    add_grid(wb, ["North"], ["Kitchen"], top=1)
    assert wb["Summary"]["Z1"].value == "keep me" and wb.sheetnames.count("Summary") == 1, "use the existing Summary sheet."
