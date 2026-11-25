import math

import pandas as pd
import pytest

from solution import to_wide


def monthly():
    return pd.DataFrame({
        "store_id": ["S2", "S1", "S1", "S2", "S1", "S3"],
        "month": ["2025-02", "2025-01", "2025-02", "2025-01", "2025-03", "2025-03"],
        "sales": [30, 10, 15, 25, 12, 7],
    })


def test_shape_and_labels():
    out = to_wide(monthly())
    assert list(out.columns) == ["store_id", "2025-01", "2025-02", "2025-03"], (
        "first column store_id, then the months in sorted order; got %s (did you forget reset_index?)" % list(out.columns))
    assert out.columns.name is None, "clear the leftover column-label name: out.columns.name = None"
    assert out["store_id"].tolist() == ["S1", "S2", "S3"], "one row per store, sorted"
    assert out.index.tolist() == [0, 1, 2], "fresh index 0, 1, 2"


def test_values_land_in_the_right_cells():
    out = to_wide(monthly()).set_index("store_id")
    assert out.loc["S1"].tolist() == [10, 15, 12], "S1's January..March sales are 10, 15, 12"
    assert out.loc["S2", "2025-01"] == 25 and out.loc["S2", "2025-02"] == 30, "S2 has 25 in January and 30 in February"
    assert out.loc["S3", "2025-03"] == 7, "S3 only has March (7)"


def test_missing_pairs_are_nan_not_zero():
    out = to_wide(monthly()).set_index("store_id")
    for store, month in [("S2", "2025-03"), ("S3", "2025-01"), ("S3", "2025-02")]:
        v = out.loc[store, month]
        assert v != 0, "%s %s is not in the data: leave it missing (NaN), do not fill 0" % (store, month)
        assert math.isnan(v), "%s %s must be NaN" % (store, month)


def test_duplicate_pair_raises_helpful_error():
    m = pd.concat([monthly(), pd.DataFrame({"store_id": ["S1"], "month": ["2025-02"], "sales": [5]})], ignore_index=True)
    with pytest.raises(ValueError) as err:
        to_wide(m)
    msg = str(err.value)
    assert "pivot_table" in msg, "the error must tell the reader to use pivot_table (with an aggregation); got: " + msg
    assert "S1" in msg and "2025-02" in msg, "the error must name the repeated pair (S1, 2025-02); got: " + msg


def test_input_unchanged():
    m = monthly()
    before = m.copy()
    to_wide(m)
    pd.testing.assert_frame_equal(m, before, obj="monthly")
