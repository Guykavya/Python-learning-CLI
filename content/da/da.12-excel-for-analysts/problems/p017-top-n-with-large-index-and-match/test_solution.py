import numpy as np
import pandas as pd
import pytest

from openpyxl import Workbook

from conftest import Book
from solution import add_top3


def make(df):
    wb = Workbook()
    ws = wb.active
    ws.title = "Products"
    ws.append(["code", "revenue"])
    for r in df.itertuples(index=False):
        ws.append(list(r))
    return wb


def top3(df):
    wb = make(df)
    add_top3(wb)
    book = Book(wb)
    return [(book.value("Top3", f"B{r}"), book.value("Top3", f"C{r}")) for r in (2, 3, 4)], wb


def test_without_ties():
    df = pd.DataFrame({"code": list("ABCDE"), "revenue": [10.0, 90.0, 70.0, 30.0, 50.0]})
    got, wb = top3(df)
    assert got == [("B", 90.0), ("C", 70.0), ("E", 50.0)], f"top three by revenue: B, C, E; got {got}"
    assert [wb["Top3"].cell(r, 1).value for r in (2, 3, 4)] == [1, 2, 3] and wb["Top3"]["B1"].value == "code", "ranks 1, 2, 3 in column A and the headers."


def test_with_ties_three_different_products():
    df = pd.DataFrame({"code": list("ABCDE"), "revenue": [100.0, 80.0, 80.0, 80.0, 50.0]})
    got, _ = top3(df)
    assert [c for c, _ in got] == ["A", "B", "C"], f"with a three-way tie the first two in file order follow A: A, B, C (all different); got {got}"
    expected = df.nlargest(3, "revenue", keep="first")
    assert [c for c, _ in got] == expected["code"].tolist() and [v for _, v in got] == expected["revenue"].tolist(), "same as pandas nlargest(3, keep='first')."


def test_top_value_tied_at_the_top():
    df = pd.DataFrame({"code": list("ABCD"), "revenue": [60.0, 60.0, 60.0, 10.0]})
    got, _ = top3(df)
    assert [c for c, _ in got] == ["A", "B", "C"], f"all three tied at the top: A, B, C; got {got}"


def test_revenue_is_the_real_revenue_not_the_key():
    df = pd.DataFrame({"code": list("ABCD"), "revenue": [80.0, 80.0, 80.0, 1.0]})
    got, _ = top3(df)
    assert [v for _, v in got] == [80.0, 80.0, 80.0], "column C of Top3 shows the revenue, not the helper key (79.999999...)."


def test_helper_column_and_error():
    df = pd.DataFrame({"code": list("ABCD"), "revenue": [5.0, 5.0, 3.0, 1.0]})
    wb = make(df)
    add_top3(wb)
    assert wb["Products"]["C1"].value == "rank_key" and "COUNTIF" in wb["Products"]["C3"].value.upper(), "helper column C with a COUNTIF."
    with pytest.raises(ValueError, match="need at least 3 products"):
        add_top3(make(df.head(2)))
