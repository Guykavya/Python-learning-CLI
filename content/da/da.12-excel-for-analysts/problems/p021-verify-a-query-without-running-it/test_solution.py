import numpy as np
import pandas as pd
import pytest

from solution import compare_fingerprints, fingerprint_table

DF = pd.DataFrame({"order_id": ["O1", "O2", "O3", "O3"], "region": ["N", None, "S", "S"], "units": [3, 5, None, 2], "revenue": [10.5, 20.25, 7.0, 7.0]})


def test_fingerprint_contents_and_order():
    fp = fingerprint_table(DF, keys=["order_id", "region"])
    assert list(fp) == ["rows", "columns", "sum(units)", "sum(revenue)", "blank(order_id)", "blank(region)", "blank(units)", "blank(revenue)", "distinct(order_id)", "distinct(region)"], f"entries in the order of the statement; got {list(fp)}"
    assert fp["rows"] == 4 and fp["columns"] == ["order_id", "region", "units", "revenue"]
    assert fp["sum(units)"] == 10.0 and fp["sum(revenue)"] == 44.75, "sums of the numeric columns (NaN skipped)."
    assert (fp["blank(region)"], fp["blank(units)"], fp["blank(order_id)"]) == (1, 1, 0), "blanks of every column."
    assert (fp["distinct(order_id)"], fp["distinct(region)"]) == (3, 2), "distinct values of the keys (the missing region is not counted)."


def test_sums_are_rounded_and_types_are_plain():
    fp = fingerprint_table(pd.DataFrame({"x": [0.1] * 3}))
    assert fp["sum(x)"] == 0.3, "round the sum to 4 decimals: 0.30000000000000004 becomes 0.3."
    assert type(fp["rows"]) is int and type(fp["sum(x)"]) is float and type(fp["blank(x)"]) is int


def test_identical_tables_have_no_differences():
    assert compare_fingerprints(fingerprint_table(DF, ["order_id"]), fingerprint_table(DF.copy(), ["order_id"])) == []


def test_differences_in_plain_words():
    a = fingerprint_table(DF, ["order_id"])
    b = fingerprint_table(DF.iloc[:3].assign(extra=1), ["order_id"])
    got = compare_fingerprints(a, b)
    assert got[0] == "rows: 4 against 3", f"first the row count; got {got}"
    assert "columns: ['order_id', 'region', 'units', 'revenue'] against ['order_id', 'region', 'units', 'revenue', 'extra']" in got
    assert "sum(revenue): 44.75 against 37.75" in got and "blank(extra): only in the second" not in got[:2]
    assert got[-2:] == ["sum(extra): only in the second", "blank(extra): only in the second"], f"entries only in the second come last; got {got[-3:]}"


def test_entries_only_in_the_first():
    a = fingerprint_table(DF, ["order_id"])
    b = fingerprint_table(DF)
    assert "distinct(order_id): only in the first" in compare_fingerprints(a, b)
