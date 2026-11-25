import numpy as np
import pandas as pd
import pandera.pandas as pa
import pytest

from solution import split_valid

SCHEMA = pa.DataFrameSchema({
    "id": pa.Column(int, unique=True),
    "age": pa.Column(float, pa.Check.in_range(18, 75), nullable=True),
    "city": pa.Column(str, pa.Check.isin(["Pune", "Delhi"])),
})


def frame(index=None):
    return pd.DataFrame({"id": [1, 2, 2, 4, 5, 6],
                         "age": [20.0, 80.0, 30.0, np.nan, 17.0, 40.0],
                         "city": ["Pune", "Goa", "Delhi", "Pune", "Pune", "Delhi"]}, index=index)


def test_worked_example():
    valid, q = split_valid(frame(), SCHEMA)
    assert valid.index.tolist() == [0, 3, 5], "rows 0, 3, 5 break nothing (a missing age is allowed). Got valid rows %s." % valid.index.tolist()
    assert q.index.tolist() == [1, 2, 4], "rows 1, 2 (duplicate id), 4 (age 17) are quarantined. Got %s." % q.index.tolist()
    assert q["reasons"].tolist() == ["age, city, id", "id", "age"], (
        "reasons are the failing column names, sorted, without repeats, joined with ', '. Got %s." % q["reasons"].tolist())


def test_columns_and_values_are_kept():
    d = frame()
    valid, q = split_valid(d, SCHEMA)
    assert list(valid.columns) == ["id", "age", "city"], "valid keeps the original columns only."
    assert list(q.columns) == ["id", "age", "city", "reasons"], "quarantine = original columns + reasons (last)."
    pd.testing.assert_frame_equal(valid, d.loc[[0, 3, 5]], obj="the valid rows")
    pd.testing.assert_frame_equal(q[["id", "age", "city"]], d.loc[[1, 2, 4]], obj="the quarantined rows (without reasons)")


def test_every_row_exactly_once_and_original_labels():
    d = frame(index=[100, 101, 102, 103, 104, 105])
    valid, q = split_valid(d, SCHEMA)
    assert valid.index.tolist() == [100, 103, 105] and q.index.tolist() == [101, 102, 104], (
        "keep the original index labels. Got valid %s, quarantine %s." % (valid.index.tolist(), q.index.tolist()))
    assert sorted(valid.index.tolist() + q.index.tolist()) == d.index.tolist(), "valid + quarantine must be all the rows, once each."


def test_nothing_fails():
    d = frame().loc[[0, 3, 5]]
    valid, q = split_valid(d, SCHEMA)
    pd.testing.assert_frame_equal(valid, d, obj="valid when nothing fails")
    assert len(q) == 0 and "reasons" in q.columns, "the quarantine is empty but still has the reasons column."


def test_everything_fails():
    d = pd.DataFrame({"id": [1, 1], "age": [99.0, 99.0], "city": ["X", "Y"]})
    valid, q = split_valid(d, SCHEMA)
    assert len(valid) == 0 and q["reasons"].tolist() == ["age, city, id", "age, city, id"]


def test_a_missing_column_still_raises():
    d = frame().drop(columns=["city"])
    with pytest.raises((pa.errors.SchemaErrors, pa.errors.SchemaError)):
        split_valid(d, SCHEMA)


def test_input_not_changed():
    d = frame()
    before = d.copy()
    split_valid(d, SCHEMA)
    pd.testing.assert_frame_equal(d, before, obj="the input frame")
