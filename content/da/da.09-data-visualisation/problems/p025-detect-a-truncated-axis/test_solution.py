import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")

from solution import is_truncated, lie_factor, visual_change


def bars(bottom=None, top=None):
    fig, ax = plt.subplots()
    ax.bar(["2023", "2024"], [2.108, 2.344])
    ax.set_ylim(bottom, top)
    return ax


def test_honest_axis():
    ax = bars(0, 2.6)
    assert visual_change(ax) == pytest.approx(0.1119, abs=1e-3), "from an axis at 0 the drawn change equals the data change, 11.2%."
    assert lie_factor(ax) == pytest.approx(1.0), "an honest chart has a lie factor of 1."
    assert is_truncated(ax) is False, "an axis from 0 is not truncated."


def test_truncated_axis():
    ax = bars(2.0, 2.4)
    assert visual_change(ax) == pytest.approx(0.344 / 0.108 - 1, abs=1e-6), "measure each bar from the bottom of the axis (2.0): 0.108 and 0.344."
    assert lie_factor(ax) == pytest.approx((0.344 / 0.108 - 1) / (2.344 / 2.108 - 1), rel=1e-6), "lie factor = visual change / data change (about 19.5)."
    assert is_truncated(ax) is True, "an axis from 2.0 cuts the bars: truncated."


def test_axis_below_zero_is_fine():
    assert is_truncated(bars(-1, 3)) is False, "an axis that starts below 0 still shows the whole bar."


def test_horizontal_bars():
    fig, ax = plt.subplots()
    ax.barh(["a", "b", "c"], [50, 60, 55])
    ax.set_xlim(40, 65)
    assert is_truncated(ax) is True, "horizontal bars: look at the left end of the x axis."
    ax.set_xlim(0, 65)
    assert is_truncated(ax) is False


def test_line_chart_is_not_truncated():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [100, 102, 101])
    ax.set_ylim(99, 103)
    assert is_truncated(ax) is False, "a line chart has no bars to cut off."
