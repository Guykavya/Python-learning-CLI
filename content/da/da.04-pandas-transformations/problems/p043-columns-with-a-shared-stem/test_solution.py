import random

import pandas as pd
import pytest

from solution import yearly_long


def slow_yearly_long(df):
    """Loop version: read every column name, split it into stem and year."""
    rows = {}
    for record in df.to_dict("records"):
        store = record["store_id"]
        for col, value in record.items():
            if col == "store_id":
                continue
            stem, year = col.split("_")
            rows.setdefault((store, int(year)), {})[stem] = value
    keys = sorted(rows)
    return pd.DataFrame({"store_id": [k[0] for k in keys], "year": [k[1] for k in keys],
                         "sales": [rows[k]["sales"] for k in keys], "units": [rows[k]["units"] for k in keys]})


def random_report(seed):
    rng = random.Random(seed)
    stores = ["S%d" % i for i in range(1, rng.randint(1, 6) + 1)]
    rng.shuffle(stores)
    first = rng.randint(2018, 2023)
    years = list(range(first, first + rng.randint(1, 4)))
    data = {"store_id": stores}
    cols = [(stem, y) for stem in ["sales", "units"] for y in years]
    rng.shuffle(cols)
    for stem, y in cols:
        data["%s_%d" % (stem, y)] = [rng.randint(0, 900) for _ in stores]
    return pd.DataFrame(data)


def fixed():
    return pd.DataFrame({"store_id": ["S2", "S1", "S3"], "sales_2023": [200, 100, 50], "units_2023": [20, 10, 5],
                         "sales_2024": [190, 110, 60], "units_2024": [18, 12, 6]})


def test_columns_and_dtypes():
    out = yearly_long(fixed())
    assert list(out.columns) == ["store_id", "year", "sales", "units"], (
        "exactly store_id, year, sales, units; got %s (forgot reset_index, or used melt only?)" % list(out.columns))
    assert str(out["year"].dtype) == "int64", "year must be an integer, not text (got %s)" % out["year"].dtype


def test_fixed_values():
    out = yearly_long(fixed())
    assert len(out) == 6, "3 stores x 2 years = 6 rows; got %d (did you pass sep='_'?)" % len(out)
    assert out.values.tolist() == [["S1", 2023, 100, 10], ["S1", 2024, 110, 12], ["S2", 2023, 200, 20],
                                   ["S2", 2024, 190, 18], ["S3", 2023, 50, 5], ["S3", 2024, 60, 6]], (
        "one row per store and year, sorted by store then year, with that year's sales and units")
    assert out.index.tolist() == list(range(6)), "fresh index after sorting"


@pytest.mark.parametrize("seed", range(15))
def test_matches_loop_version(seed):
    df = random_report(seed)
    pd.testing.assert_frame_equal(yearly_long(df), slow_yearly_long(df), obj="yearly_long vs the loop (seed %d)" % seed)


def test_input_unchanged():
    df = fixed()
    before = df.copy()
    yearly_long(df)
    pd.testing.assert_frame_equal(df, before, obj="the input report")
