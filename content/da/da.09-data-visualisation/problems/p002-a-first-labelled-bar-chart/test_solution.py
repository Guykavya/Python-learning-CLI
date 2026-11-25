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

from solution import bar_chart

CATS = ["Harbour", "Airport", "Campus", "Mall"]
VALS = [3200, 4100, 1500, 2800]


def build():
    return bar_chart(CATS, VALS, "Revenue by store", "Revenue (USD)")


def test_returns_the_figure():
    fig = build()
    assert fig is not None, "return fig: the function returned None (do not call plt.show())."
    assert len(fig.axes) == 1, "one chart needs exactly one Axes."


def test_one_bar_per_category_with_the_right_heights():
    ax = build().axes[0]
    assert len(ax.patches) == len(CATS), f"expected {len(CATS)} bars, found {len(ax.patches)}."
    heights = [float(p.get_height()) for p in ax.patches]
    assert heights == [float(v) for v in VALS], f"bar heights should be {VALS}, got {heights}."


def test_labels_in_the_given_order():
    fig = build()
    fig.canvas.draw()
    labels = [t.get_text() for t in fig.axes[0].get_xticklabels()]
    assert labels == CATS, f"x tick labels should keep the given order {CATS}, got {labels} (do not sort)."


def test_title_and_ylabel():
    ax = build().axes[0]
    assert ax.get_title() == "Revenue by store", f"the title is missing or wrong: {ax.get_title()!r}."
    assert ax.get_ylabel() == "Revenue (USD)", f"the y label is missing or wrong: {ax.get_ylabel()!r}."


def test_other_data():
    fig = bar_chart(["a", "b", "c"], [3, 1, 2], "T", "Y")
    assert [float(p.get_height()) for p in fig.axes[0].patches] == [3.0, 1.0, 2.0], "bars must follow the input values, not fixed numbers."
