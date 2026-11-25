import numpy as np
import pandas as pd
import pytest

from solution import check_pivot

EXP = pd.DataFrame({"Kitchen": [1200.0, 800.0, 2000.0], "Living": [500.5, 300.25, 800.75], "Grand Total": [1700.5, 1100.25, 2800.75]},
                   index=["North", "South", "Grand Total"])


def test_matching_pivot_with_different_labels_and_rounding():
    pasted = EXP.round(2).copy()
    pasted.index = ["north ", " South", "Total"]
    pasted.columns = ["kitchen", "LIVING", "grand total"]
    assert check_pivot(EXP, pasted, tol=0.006) == [], "labels differ only in case, spaces and 'Total' against 'Grand Total': the values match."


def test_one_wrong_cell():
    pasted = EXP.copy()
    pasted.loc["North", "Kitchen"] = 1150.5
    assert check_pivot(EXP, pasted) == ["north / kitchen: expected 1,200.00, pasted 1,150.50"], f"got {check_pivot(EXP, pasted)}"


def test_missing_row_and_extra_column():
    pasted = EXP.drop(index="South").copy()
    pasted["Outdoor"] = 0.0
    got = check_pivot(EXP, pasted)
    assert got == ["row only in expected: south", "column only in pasted: outdoor"], f"a missing row and an extra column, and no cell messages for the missing row; got {got}"


def test_tolerance_is_inclusive():
    pasted = EXP.copy()
    pasted.loc["South", "Living"] += 0.005
    assert check_pivot(EXP, pasted, tol=0.005 + 1e-9) == [], "a difference within the tolerance is fine."
    assert len(check_pivot(EXP, pasted, tol=0.001)) == 1, "a difference above the tolerance is reported."


def test_order_of_messages():
    pasted = EXP.copy()
    pasted.loc["Grand Total", "Kitchen"] = 1.0
    pasted.loc["North", "Living"] = 1.0
    got = check_pivot(EXP, pasted)
    assert [g.split(":")[0] for g in got] == ["north / living", "grand total / kitchen"], f"cells are reported in the order of the expected table (rows, then columns); got {got}"
