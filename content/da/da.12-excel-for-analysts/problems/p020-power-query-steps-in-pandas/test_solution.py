import numpy as np
import pandas as pd
import pytest

import io

from solution import apply_steps

RAW = """order_id,order_date,region,units,unit_price
O1, 2024-01-05 ,north ,3,10.5
O2,2024-01-06,South,"1,200",8.25
O3,2024-01-06,SOUTH,n/a,8.25
O4,2024-02-10,East,5,
O5,2024-02-11,East,7,12
"""


def raw():
    return pd.read_csv(io.StringIO(RAW), dtype=str, keep_default_na=False)


STEPS = [
    {"step": "trim", "columns": ["order_date", "region"]},
    {"step": "proper", "columns": ["region"]},
    {"step": "replace", "column": "units", "old": ",", "new": ""},
    {"step": "change_type", "types": {"order_date": "date", "units": "int", "unit_price": "float"}},
    {"step": "filter_blanks", "column": "units"},
    {"step": "filter_blanks", "column": "unit_price"},
]


def test_cleaning_steps_give_the_expected_table():
    got = apply_steps(raw(), STEPS)
    assert got["order_id"].tolist() == ["O1", "O2", "O5"], f"O3 (units 'n/a') and O4 (no price) are dropped; got {got['order_id'].tolist()}"
    assert got["region"].tolist() == ["North", "South", "East"], "trim, then proper: 'north ' -> 'North', 'South' stays."
    assert got["units"].tolist() == [3, 1200, 7] and got["unit_price"].tolist() == [10.5, 8.25, 12.0], "the thousands separator is removed before the type change."
    assert got["order_date"].tolist() == [pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-06"), pd.Timestamp("2024-02-11")]
    assert list(got.index) == [0, 1, 2], "reset the index."


def test_input_is_not_changed():
    df = raw()
    before = df.copy()
    apply_steps(df, STEPS)
    pd.testing.assert_frame_equal(df, before)


def test_bad_values_become_nan_before_filtering():
    got = apply_steps(raw(), STEPS[:4])
    assert got["units"].isna().tolist() == [False, False, True, False, False] and got["units"].dtype == float, "a value that fails to convert is NaN, so the column stays a float column."


def test_unpivot_and_group():
    wide = pd.DataFrame({"region": ["N", "S"], "jan": [1.0, 5.0], "feb": [2.0, 6.0]})
    long = apply_steps(wide, [{"step": "unpivot", "id_columns": ["region"], "var_name": "month", "value_name": "revenue"}])
    assert long.shape == (4, 3) and set(long.columns) == {"region", "month", "revenue"}, f"melt gives 4 rows x 3 columns; got {long.shape}"
    out = apply_steps(long, [{"step": "group", "by": ["region"], "aggregations": {"total": ("revenue", "sum"), "n": ("revenue", "count")}}])
    assert out.to_dict("list") == {"region": ["N", "S"], "total": [3.0, 11.0], "n": [2, 2]}, f"got {out.to_dict('list')}"


def test_unknown_step():
    with pytest.raises(ValueError, match="unknown step: explode"):
        apply_steps(raw(), [{"step": "explode"}])
