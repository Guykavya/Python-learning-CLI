import numpy as np
import pandas as pd
import pytest

from datetime import date, datetime

from openpyxl import Workbook

from solution import audit_column


def sheet(values):
    ws = Workbook().active
    ws.append(["units"])
    for v in values:
        ws.append([v])
    return ws


def test_each_kind_once():
    ws = sheet([10, "12", None, "", datetime(2024, 3, 15), "abc", 3.5])
    got = audit_column(ws, "A")
    assert got == {"numbers": 2, "text_numbers": 1, "blanks": 1, "empty_strings": 1, "dates": 1, "other_text": 1, "booleans": 0}, f"got {got}"


def test_text_numbers_with_spaces_and_signs():
    got = audit_column(sheet(["7", " 3.5 ", "-2", "1e3", "12 kg"]), "A")
    assert got["text_numbers"] == 4 and got["other_text"] == 1, f"'7', ' 3.5 ', '-2' and '1e3' are numbers stored as text; '12 kg' is text. Got {got}"


def test_booleans_and_dates_are_not_numbers():
    got = audit_column(sheet([True, False, date(2024, 1, 1), 5]), "A")
    assert got["booleans"] == 2 and got["dates"] == 1 and got["numbers"] == 1, f"a bool is not a number; got {got}"


def test_header_is_skipped_and_counts_add_up():
    ws = sheet(["x", 1, None])
    assert sum(audit_column(ws, "A").values()) == 3, "the header row is not counted: 3 rows below it."


def test_other_column_and_empty_sheet():
    ws = sheet([1, 2])
    ws["C1"], ws["C2"] = "h", "5"
    assert audit_column(ws, "C")["text_numbers"] == 1 and audit_column(ws, "C")["blanks"] == 1, "column C has '5' and an empty cell below the header."
    assert sum(audit_column(sheet([]), "A").values()) == 0, "only a header: all counts are 0."
