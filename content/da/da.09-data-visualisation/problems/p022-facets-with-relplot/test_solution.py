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

import seaborn as sns

from solution import store_lines


def make(stores=("B", "A", "C", "D")):
    rows = []
    for k, s in enumerate(stores):
        for w in range(6):
            rows.append({"week": w, "store": s, "revenue": 100.0 * (k + 1) + 10 * w})
    return pd.DataFrame(rows)


def test_returns_a_facetgrid():
    g = store_lines(make())
    assert isinstance(g, sns.FacetGrid), f"return the FacetGrid that relplot gives you, not {type(g).__name__}."


def test_one_panel_per_store_with_plain_titles():
    g = store_lines(make())
    titles = [ax.get_title() for ax in g.axes.flat]
    assert sorted(titles) == ["A", "B", "C", "D"], f"panel titles should be just the store names, got {titles} (g.set_titles('{{col_name}}'))."


def test_shared_y_axis():
    g = store_lines(make())
    axes = list(g.axes.flat)
    for other in axes[1:]:
        assert axes[0].get_shared_y_axes().joined(axes[0], other), "the panels must share one y axis so that they can be compared."


def test_each_panel_has_one_line_of_six_points():
    g = store_lines(make())
    for ax in g.axes.flat:
        assert len(ax.lines) == 1, f"{ax.get_title()}: one line per panel (errorbar=None draws no interval), found {len(ax.lines)}."
        assert len(ax.lines[0].get_xdata()) == 6, "each line has the six weekly points."


def test_wraps_after_three():
    g = store_lines(make())
    assert g.axes.shape == (2, 3) or len(g.axes.flat) == 4, "four stores with col_wrap=3 fill a 2 x 3 grid."
    assert len(g.axes.flat) == 4, f"expected 4 panels, got {len(g.axes.flat)}."
