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

from solution import category_bars

DF = pd.DataFrame({"store": ["A", "A", "B", "C", "B"], "revenue": [100.0, 50.0, 300.0, 220.0, 100.0]})


def top_to_bottom(ax):
    ax.figure.canvas.draw()
    labels = [t.get_text() for t in ax.get_yticklabels()]
    pos = [(p.get_y() + p.get_height() / 2, float(p.get_width())) for p in ax.patches]
    name_by_pos = dict(zip([round(p[0], 6) for p in pos], labels))
    inverted = ax.yaxis_inverted()
    ordered = sorted(pos, key=lambda p: p[0], reverse=not inverted)       # visual top first
    return [(name_by_pos[round(p[0], 6)], p[1]) for p in ordered]


def test_one_bar_per_category_with_totals():
    ax = category_bars(DF, "store", "revenue").axes[0]
    assert len(ax.patches) == 3, f"one bar per store: expected 3 bars, found {len(ax.patches)} (add the rows of a store together)."
    assert sorted(float(p.get_width()) for p in ax.patches) == [150.0, 220.0, 400.0], "bar lengths must be the totals 150, 220, 400."


def test_largest_on_top():
    ax = category_bars(DF, "store", "revenue").axes[0]
    order = top_to_bottom(ax)
    assert [n for n, _ in order] == ["B", "C", "A"], f"from the top the bars should be B (400), C (220), A (150); got {order}. barh draws the first bar at the bottom."


def test_axis_starts_at_zero():
    ax = category_bars(DF, "store", "revenue").axes[0]
    assert ax.get_xlim()[0] <= 0, f"the value axis must start at 0, it starts at {ax.get_xlim()[0]:g}."


def test_xlabel_names_the_value():
    ax = category_bars(DF, "store", "revenue").axes[0]
    assert ax.get_xlabel() == "revenue", f"the x label should be the column name 'revenue', got {ax.get_xlabel()!r}."


def test_other_columns():
    df = pd.DataFrame({"city": ["x", "y"], "units": [1, 9]})
    ax = category_bars(df, "city", "units").axes[0]
    assert top_to_bottom(ax)[0][0] == "y", "the function must use the column names it is given."
