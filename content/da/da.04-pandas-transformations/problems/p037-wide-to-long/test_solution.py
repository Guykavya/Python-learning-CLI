import math

import pandas as pd

from solution import to_long


def wide():
    return pd.DataFrame({
        "store_id": ["S2", "S1", "S3"],
        "2025-02": [5.0, 1.0, 4.0],
        "2025-01": [7.0, 2.0, 3.0],
        "2025-03": [9.0, None, 6.0],
    })


def test_columns_and_length():
    out = to_long(wide())
    assert list(out.columns) == ["store_id", "month", "sales"], (
        "name the new columns with var_name='month' and value_name='sales'; got %s" % list(out.columns))
    assert len(out) == 9, "3 stores x 3 month columns = 9 rows (got %d)" % len(out)


def test_sorted_by_store_then_calendar_month():
    out = to_long(wide())
    assert out["store_id"].tolist() == ["S1"] * 3 + ["S2"] * 3 + ["S3"] * 3, "sort by store_id first"
    assert out["month"].tolist() == ["2025-01", "2025-02", "2025-03"] * 3, (
        "inside each store the months must be in calendar order, even though the wide columns were Feb, Jan, Mar")
    assert out.index.tolist() == list(range(9)), "reset the index after sorting"


def test_values_follow_their_cells():
    out = to_long(wide())
    got = {(s, m): v for s, m, v in out.itertuples(index=False)}
    assert got[("S1", "2025-01")] == 2.0 and got[("S2", "2025-02")] == 5.0 and got[("S3", "2025-03")] == 6.0, (
        "each sales value must stay with its own store and month")


def test_missing_cell_kept():
    out = to_long(wide())
    row = out[(out["store_id"] == "S1") & (out["month"] == "2025-03")]
    assert len(row) == 1, "S1's missing March cell must stay a row (do not dropna here)"
    assert math.isnan(row["sales"].iloc[0]), "and its sales value stays missing, not 0"


def test_input_unchanged():
    w = wide()
    before = w.copy()
    to_long(w)
    pd.testing.assert_frame_equal(w, before, obj="wide")
