import numpy as np
import pandas as pd
import pytest

import io
from datetime import datetime

from openpyxl import Workbook, load_workbook

from solution import write_safe

UNTRUSTED = ["Asha", '=HYPERLINK("http://example.com","Click")', "+44 123", "@SUM(1,1)", "-5 widgets", "=1+1", "", "a=b"]


def roundtrip(values):
    wb = Workbook()
    ws = wb.active
    for i, v in enumerate(values, 1):
        write_safe(ws, i, 1, v)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return load_workbook(buf).active


def test_dangerous_text_stays_text_and_unchanged():
    back = roundtrip(UNTRUSTED)
    for i, v in enumerate(UNTRUSTED, 1):
        cell = back.cell(i, 1)
        if v == "":
            continue
        assert cell.data_type != "f", f"{v!r} was stored as a formula: Excel would run it when the file is opened."
        assert cell.value == v, f"the text must come back unchanged: {v!r}, got {cell.value!r}"


def test_numbers_dates_booleans_and_none_are_unchanged():
    values = [-5, 3.5, True, datetime(2024, 3, 15), None, 0]
    back = roundtrip(values)
    assert back["A1"].value == -5 and back["A1"].data_type == "n", "a negative NUMBER stays a number."
    assert back["A2"].value == 3.5 and back["A3"].value is True and back["A4"].value == datetime(2024, 3, 15) and back["A5"].value is None


def test_returns_the_cell():
    ws = Workbook().active
    cell = write_safe(ws, 2, 3, "=A1")
    assert cell is ws["C2"] and cell.data_type == "s", "return the cell that was written."


def test_a_real_formula_is_not_what_we_want_here():
    ws = Workbook().active
    write_safe(ws, 1, 1, "=1+1")
    assert ws["A1"].data_type == "s", "write_safe never writes formulas: use ws[cell] = '=...' for your own formulas."
