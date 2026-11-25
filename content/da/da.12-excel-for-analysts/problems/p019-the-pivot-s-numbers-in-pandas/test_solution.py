import numpy as np
import pandas as pd
import pytest

from solution import pivot_expected

ORDERS = pd.DataFrame({
    "region": ["north", "North", "South", "East", "north", "South"],
    "category": ["Kitchen", "living", "Kitchen", "Living", "Kitchen", "living"],
    "revenue": [100.004, 50.5, 70.25, 20.0, 5.331, 8.0],
})


def test_order_totals_and_values():
    pt = pivot_expected(ORDERS)
    assert list(pt.index) == ["East", "north", "North", "South", "Grand Total"] or list(pt.index) == ["East", "North", "north", "South", "Grand Total"], f"rows alphabetical ignoring case, Grand Total last; got {list(pt.index)}"
    assert list(pt.columns) == ["Kitchen", "Living", "living", "Grand Total"] or list(pt.columns) == ["Kitchen", "living", "Living", "Grand Total"], f"columns likewise; got {list(pt.columns)}"
    assert pt.loc["Grand Total", "Grand Total"] == pytest.approx(round(ORDERS["revenue"].sum(), 2)), "the corner is the total of everything."


def test_simple_case_hand_values():
    d = pd.DataFrame({"region": ["b", "A", "b", "c"], "category": ["x", "x", "y", "x"], "revenue": [1.005, 2.0, 3.0, 4.0]})
    pt = pivot_expected(d)
    assert list(pt.index) == ["A", "b", "c", "Grand Total"] and list(pt.columns) == ["x", "y", "Grand Total"], f"got {list(pt.index)}, {list(pt.columns)}"
    assert pt.loc["b", "x"] == 1.0 or pt.loc["b", "x"] == 1.01, "rounded to two decimals."
    assert pt.loc["A", "y"] == 0.0 and not pt.isna().any().any(), "no sales in a combination: 0.0, not NaN."
    assert pt.loc["Grand Total", "x"] == pytest.approx(round(1.005 + 2.0 + 4.0, 2)) and pt.loc["b", "Grand Total"] == pytest.approx(round(1.005 + 3.0, 2)), "margins are sums of the unrounded values, rounded once."


def test_rounding_happens_once_at_the_end():
    d = pd.DataFrame({"region": ["a"] * 3, "category": ["x"] * 3, "revenue": [0.004, 0.004, 0.004]})
    assert pivot_expected(d).loc["Grand Total", "Grand Total"] == 0.01, "0.012 rounds to 0.01; rounding each line first would give 0.0."
