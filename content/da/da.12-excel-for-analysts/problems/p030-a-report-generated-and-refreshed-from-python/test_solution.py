import numpy as np
import pandas as pd
import pytest

import time

from conftest import Book, XlError, lint_workbook, make_data, verify_report
from solution import build_report


@pytest.fixture(scope="module")
def report():
    orders, products = make_data()
    return orders, products, build_report(orders, products)


def test_sheets_and_input(report):
    orders, products, wb = report
    assert wb.sheetnames == ["Summary", "Orders", "Products", "Inputs"], f"sheets in this order; got {wb.sheetnames}"
    assert wb["Inputs"]["A1"].value == "Target gross margin" and wb["Inputs"]["B1"].value == 0.40, "the target margin is an input cell."
    assert len(list(wb["Orders"].iter_rows(min_row=2))) == len(orders), "one row per order line."


def test_orders_sheet_has_formulas_not_values(report):
    _, products, wb = report
    wo = wb["Orders"]
    k = len(products)
    assert [c.value for c in wo[1]][7:] == ["category", "unit_cost", "revenue", "cost", "margin"], "headers of the calculated columns."
    assert wo["H2"].value.replace(" ", "") == f"=XLOOKUP(D2,Products!$A$2:$A${k + 1},Products!$C$2:$C${k + 1})", f"H2 lookup, got {wo['H2'].value!r}"
    assert [wo[f"{c}3"].value for c in "JKL"] == ["=E3*F3*(1-G3)", "=E3*I3", "=J3-K3"], "revenue, cost, margin formulas."


def test_every_number_matches_pandas(report):
    orders, products, wb = report
    problems = verify_report(wb, orders, products, 0.40)
    assert problems == [], f"the Summary must equal pandas: {problems[:5]}"


def test_the_lint_finds_nothing(report):
    orders, _, wb = report
    assert lint_workbook(wb, len(orders)) == [], f"lint: {lint_workbook(wb, len(orders))}"


def test_no_errors_in_the_orders_sheet(report):
    orders, _, wb = report
    bk = Book(wb)
    bad = [r for r in range(2, len(orders) + 2) if any(isinstance(bk.value("Orders", f"{c}{r}"), XlError) for c in "HIJKL")]
    assert bad == [], f"error values in Orders rows {bad[:5]} (is every product code found?)"


def test_a_longer_dataset_after_a_refresh():
    orders, products = make_data(seed=11, n=450)
    wb = build_report(orders, products)
    assert wb.defined_names["Rev"].attr_text == "Orders!$J$2:$J$451", f"after a refresh with 450 orders the names must end at row 451; got {wb.defined_names['Rev'].attr_text}"
    assert lint_workbook(wb, 450) == [], f"lint on the refreshed workbook: {lint_workbook(wb, 450)}"
    assert verify_report(wb, orders, products, 0.40) == [], "every number matches pandas for the longer data set too."


def test_status_follows_the_target_margin():
    orders, products = make_data(seed=5, n=120)
    high, low = build_report(orders, products, target_margin=0.99), build_report(orders, products, target_margin=0.0)
    assert Book(high).value("Summary", "B6") == "below target" and Book(low).value("Summary", "B6") == "on target", "the status compares the margin % with the Inputs cell."
    assert verify_report(high, orders, products, 0.99) == [] and verify_report(low, orders, products, 0.0) == []


def test_conditional_format_and_speed():
    orders, products = make_data(seed=6, n=100)
    t = time.perf_counter()
    wb = build_report(orders, products)
    cf = [(str(c.sqref), r.operator, r.formula) for c in wb["Summary"].conditional_formatting for r in c.rules]
    assert cf == [("B6", "equal", ['"below target"'])], f"conditional format on B6; got {cf}"
    verify_report(wb, orders, products)
    assert time.perf_counter() - t < 30, "building and checking 100 lines should take a few seconds."
