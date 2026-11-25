import math

import pandas as pd
import pytest

from solution import region_month_table


def items():
    return pd.DataFrame({
        "order_id": [1, 1, 2, 3, 4, 5, 6],
        "region": ["north", "north", "north", "west", "west", "south", "north"],
        "month": ["2025-01", "2025-01", "2025-02", "2025-01", "2025-03", "2025-02", "2025-01"],
        "revenue": [100.0, 50.0, 30.0, 20.0, 80.0, 10.0, 5.0],
    })


def test_labels():
    t = region_month_table(items())
    assert t.index.tolist() == ["north", "south", "west", "Total"], (
        "rows: sorted regions then 'Total' (margins_name='Total'); got %s" % t.index.tolist())
    assert t.columns.tolist() == ["2025-01", "2025-02", "2025-03", "Total"], "columns: sorted months then 'Total'"


def test_cells_are_sums():
    t = region_month_table(items())
    assert t.loc["north", "2025-01"] == pytest.approx(155.0), (
        "north in January has three lines 100 + 50 + 5 = 155: use aggfunc='sum' (the default is the MEAN)")
    assert t.loc["north", "2025-02"] == pytest.approx(30.0)
    assert t.loc["west", "2025-03"] == pytest.approx(80.0)


def test_empty_cells_are_zero():
    t = region_month_table(items())
    for r, m in [("north", "2025-03"), ("south", "2025-01"), ("south", "2025-03"), ("west", "2025-02")]:
        v = t.loc[r, m]
        assert not math.isnan(v), "%s had no sales in %s: show 0 (fill_value=0), not NaN" % (r, m)
        assert v == 0


def test_totals():
    t = region_month_table(items())
    assert t.loc["north", "Total"] == pytest.approx(185.0), "north's row total is 155 + 30 = 185"
    assert t.loc["Total", "2025-01"] == pytest.approx(175.0), "January's column total is 155 + 20 = 175"
    assert t.loc["Total", "Total"] == pytest.approx(items()["revenue"].sum()), "the bottom-right cell must equal the grand total (295)"
    body = t.drop(index="Total", columns="Total")
    assert body.to_numpy().sum() == pytest.approx(295.0), "the body cells must add up to the grand total"


def test_input_unchanged():
    i = items()
    before = i.copy()
    region_month_table(i)
    pd.testing.assert_frame_equal(i, before, obj="items")
