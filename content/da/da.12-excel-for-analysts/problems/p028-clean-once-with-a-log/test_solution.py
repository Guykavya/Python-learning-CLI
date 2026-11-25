import numpy as np
import pandas as pd
import pytest

from openpyxl import Workbook

from conftest import Book
from solution import clean_orders

REGIONS = ["East", "North", "South"]
VALID = {"P01", "P02", "P05", "P07"}

DF = pd.DataFrame({
    "order_id": ["O1", "O2", "O3", "O4", "O5", "O6"],
    "region": ["north ", "South", "East", "WEST", "East", "SOUTH"],
    "units": ["7", 3, "n/a", 2, 5, "4"],
    "product_code": ["p7", "P01", "P02", "P02", "PO5", "P09"],
    "unit_price": [10.0, 20.0, 5.0, 8.0, 2.0, 4.0],
}, index=[10, 11, 12, 13, 14, 15])


def run():
    return clean_orders(DF, REGIONS, VALID)


def test_good_rows_are_cleaned_and_reindexed():
    clean, _, _ = run()
    assert clean["order_id"].tolist() == ["O1", "O2", "O5"], f"O3 (units n/a), O4 (region West) and O6 (code P09) cannot be repaired; got {clean['order_id'].tolist()}"
    assert clean["region"].tolist() == ["North", "South", "East"] and clean["units"].tolist() == [7.0, 3.0, 5.0]
    assert clean["product_code"].tolist() == ["P07", "P01", "P05"], "p7 -> P07 and PO5 -> P05."
    assert list(clean.index) == [0, 1, 2], "reset the index of the clean frame."


def test_quarantine_keeps_the_bad_rows_as_they_were():
    _, q, _ = run()
    assert list(q.index) == [12, 13, 15], f"original index kept; got {list(q.index)}"
    assert q.loc[12, "units"] == "n/a" and q.loc[13, "region"] == "WEST" and q.loc[15, "region"] == "SOUTH", "not cleaned: they are evidence."


def test_log_has_one_entry_per_changed_cell_of_a_good_row():
    _, _, log = run()
    assert list(log.columns) == ["row", "field", "old", "new", "rule"]
    got = list(zip(log["row"], log["field"]))
    assert got == [(10, "region"), (10, "units"), (10, "product_code"), (14, "product_code")], f"row 11 (O2) needed no change; got {got}"
    first = log.iloc[0]
    assert first["old"] == "north " and first["new"] == "North" and first["rule"] == "region: strip and proper case"
    assert log.iloc[1]["old"] == "7" and log.iloc[1]["new"] == 7.0 and log.iloc[1]["rule"] == "units: text to number"
    assert log.iloc[3]["old"] == "PO5" and log.iloc[3]["new"] == "P05"


def test_input_is_untouched_and_the_excel_total_matches_pandas():
    before = DF.copy()
    clean, _, _ = run()
    pd.testing.assert_frame_equal(DF, before)
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    ws.append(["order_id", "units", "unit_price", "revenue"])
    for i, r in enumerate(clean.itertuples(index=False), 2):
        ws.append([r.order_id, r.units, r.unit_price, f"=B{i}*C{i}"])
    ws["G1"] = f"=SUM(D2:D{len(clean) + 1})"
    assert Book(wb).value("Orders", "G1") == pytest.approx((clean["units"] * clean["unit_price"]).sum()), "after cleaning, the Excel total equals the pandas total."
