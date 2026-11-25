import numpy as np
import pandas as pd
import pandera.pandas as pa
import pytest

from solution import SCHEMA


def good():
    return pd.DataFrame({
        "resp_id": [1, 2, 3, 4],
        "age": [25.0, np.nan, 40.0, 75.0],
        "city": ["Pune", "Delhi", "Mumbai", "Pune"],
        "income": [30000.0, np.nan, 1000.0, 1000000.0],
        "satisfaction": [1, 5, 10, 7],
        "email": ["a@x.com", None, "b@y.org", "c@z.in"],
    })


def failing_columns(df):
    try:
        SCHEMA.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        return sorted(set(e.failure_cases["column"].dropna()))
    return []


def test_good_table_passes():
    assert failing_columns(good()) == [], (
        "the good table has missing ages, incomes and emails (allowed) and values exactly on the bounds (inclusive): it must pass. "
        "Failing columns: %s." % failing_columns(good()))
    out = SCHEMA.validate(good())
    assert out.shape == (4, 6)


def test_extra_columns_are_allowed():
    d = good().assign(note=["x", "y", "z", "w"])
    assert failing_columns(d) == [], "the schema is not strict: an extra column is fine."


BAD = {
    "duplicate resp_id": (lambda d: d.assign(resp_id=[1, 2, 2, 4]), "resp_id"),
    "age too high": (lambda d: d.assign(age=[25.0, np.nan, 40.0, 150.0]), "age"),
    "age too low": (lambda d: d.assign(age=[17.0, np.nan, 40.0, 75.0]), "age"),
    "unknown city": (lambda d: d.assign(city=["Pune", "Goa", "Mumbai", "Pune"]), "city"),
    "missing city": (lambda d: d.assign(city=["Pune", None, "Mumbai", "Pune"]), "city"),
    "income too high": (lambda d: d.assign(income=[30000.0, np.nan, 1000.0, 5000000.0]), "income"),
    "satisfaction 11": (lambda d: d.assign(satisfaction=[1, 5, 11, 7]), "satisfaction"),
    "email without @": (lambda d: d.assign(email=["a@x.com", None, "nope", "c@z.in"]), "email"),
}


@pytest.mark.parametrize("name", sorted(BAD))
def test_each_bad_table_fails_on_its_own_column(name):
    make, column = BAD[name]
    cols = failing_columns(make(good()))
    assert cols == [column], (
        "bad table '%s' must fail on exactly the column %r, but failures were reported on %s. "
        "Check the column's type, bounds, nullable and unique settings." % (name, column, cols))


def test_a_missing_column_is_reported():
    d = good().drop(columns=["income"])
    with pytest.raises((pa.errors.SchemaErrors, pa.errors.SchemaError)):
        SCHEMA.validate(d, lazy=True)
