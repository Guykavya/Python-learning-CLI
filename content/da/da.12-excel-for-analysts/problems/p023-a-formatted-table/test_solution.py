import numpy as np
import pandas as pd
import pytest

from datetime import datetime

from openpyxl import Workbook

from solution import write_df

DF = pd.DataFrame({"order_date": pd.to_datetime(["2024-03-15", "2024-03-16"]), "customer": ["Asha Traders", None],
                   "units": np.array([3, 12], dtype="int64"), "revenue": [1234.5, np.nan]})


def make(formats=None):
    ws = Workbook().active
    write_df(ws, DF, formats)
    return ws


def test_header_values_and_missing_cells():
    ws = make({"revenue": "#,##0.00"})
    assert [c.value for c in ws[1]] == ["order_date", "customer", "units", "revenue"] and all(c.font.b for c in ws[1]), "bold header in row 1."
    assert ws["A2"].value == datetime(2024, 3, 15) and ws["C3"].value == 12 and ws["D2"].value == 1234.5, "plain Python values (datetime, int, float)."
    assert ws["B3"].value is None and ws["D3"].value is None, "a missing value is an empty cell, not 'nan'."
    assert not ws["A2"].font.b, "only the header is bold."


def test_number_formats_by_column():
    ws = make({"revenue": "#,##0.00", "units": "0"})
    assert ws["D2"].number_format == "#,##0.00" and ws["D3"].number_format == "#,##0.00", "the revenue format on every data cell."
    assert ws["A2"].number_format == "yyyy-mm-dd" and ws["A3"].number_format == "yyyy-mm-dd", "a date column without an entry gets yyyy-mm-dd."
    assert ws["C2"].number_format == "0" and ws["D1"].number_format == "General", "the header cells keep the General format."
    assert ws["D2"].value == 1234.5, "the format changes the display, not the value."


def test_freeze_and_widths():
    ws = make()
    assert ws.freeze_panes == "A2", "freeze the header row."
    assert ws.column_dimensions["B"].width == len("Asha Traders") + 2, "width = longest text + 2."
    assert ws.column_dimensions["C"].width == len("units") + 2, "a narrow column is as wide as its header + 2."
    assert ws.column_dimensions["A"].width == len(str(datetime(2024, 3, 15))) + 2, "a date counts as the text of the value (2024-03-15 00:00:00, 19 characters) + 2."


def test_width_cap():
    ws = Workbook().active
    write_df(ws, pd.DataFrame({"x": ["a" * 100]}))
    assert ws.column_dimensions["A"].width == 40, "never wider than 40."
