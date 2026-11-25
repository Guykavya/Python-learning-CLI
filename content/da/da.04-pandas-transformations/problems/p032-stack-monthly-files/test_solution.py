import math

import pandas as pd

from solution import stack_months


def files():
    return {
        "2025-01": pd.DataFrame({"order_id": [101, 102], "store_id": ["S1", "S2"], "amount": [250.0, 90.0]}),
        "2025-02": pd.DataFrame({"order_id": [201, 202, 203], "store_id": ["S1", "S1", "S3"], "amount": [40.0, 60.0, 75.0]}),
        "2025-03": pd.DataFrame({"order_id": [301], "store_id": ["S2"], "amount": [120.0]}),
    }


def test_row_count_and_index():
    out = stack_months(files())
    assert len(out) == 6, "2 + 3 + 1 rows: stacking must keep every row (got %d)" % len(out)
    assert out.index.tolist() == list(range(6)), (
        "use ignore_index=True: every file starts at 0, so the plain concat repeats labels %s" % out.index.tolist())


def test_month_column_first_and_correct():
    out = stack_months(files())
    assert list(out.columns) == ["month", "order_id", "store_id", "amount"], (
        "`month` must be the FIRST column, then the file columns in order; got %s" % list(out.columns))
    assert out["month"].tolist() == ["2025-01"] * 2 + ["2025-02"] * 3 + ["2025-03"], "each row gets the key of the file it came from"
    assert out["order_id"].tolist() == [101, 102, 201, 202, 203, 301], "keep the files in dictionary order and the rows in file order"


def test_values_match():
    out = stack_months(files())
    assert out["amount"].sum() == 635.0, "the stacked amounts must add up to the sum of the files (635.0)"


def test_extra_column_becomes_missing_elsewhere():
    f = files()
    f["2025-02"] = f["2025-02"].assign(coupon=["NEW", None, "NEW"])
    out = stack_months(f)
    assert list(out.columns) == ["month", "order_id", "store_id", "amount", "coupon"], (
        "a column that only February has must be kept, after the first file's columns; got %s" % list(out.columns))
    c = out["coupon"].tolist()
    assert all(isinstance(v, float) and math.isnan(v) for v in c[:2] + c[5:]), (
        "January and March have no coupon column: their cells must be missing (NaN), not filled")
    assert c[2] == "NEW" and c[4] == "NEW", "February's coupons must be kept"


def test_single_file():
    out = stack_months({"2025-05": pd.DataFrame({"order_id": [1], "amount": [3.0]})})
    assert out.to_dict("list") == {"month": ["2025-05"], "order_id": [1], "amount": [3.0]}, "one file: the same rows with its month"


def test_inputs_unchanged():
    f = files()
    before = {k: v.copy() for k, v in f.items()}
    stack_months(f)
    for k in f:
        assert list(f[k].columns) == list(before[k].columns), "do not add `month` to the input frames; use assign (it returns a copy)"
        pd.testing.assert_frame_equal(f[k], before[k], obj="input frame " + k)
