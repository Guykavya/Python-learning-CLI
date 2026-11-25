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

from solution import trend


def make(seed, slope):
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 10, 80)
    return pd.DataFrame({"x": x, "y": slope * x + 1 + rng.normal(0, 1.5, 80)})


@pytest.mark.parametrize("seed,slope", [(0, 2.0), (1, -0.7), (2, 0.0)])
def test_drawn_slope_is_the_least_squares_slope(seed, slope):
    df = make(seed, slope)
    ax = trend(df).axes[0]
    assert len(ax.lines) >= 1, "regplot draws the fitted line as a Line2D in ax.lines."
    x, y = np.asarray(ax.lines[0].get_xdata(), float), np.asarray(ax.lines[0].get_ydata(), float)
    drawn = (y[-1] - y[0]) / (x[-1] - x[0])
    expected = np.polyfit(df["x"], df["y"], 1)[0]
    assert drawn == pytest.approx(expected, abs=1e-6), f"the drawn slope {drawn:.4f} should equal the least-squares slope {expected:.4f}: fit a straight line (order=1, no lowess)."


def test_scatter_points_are_the_data():
    df = make(3, 1.0)
    ax = trend(df).axes[0]
    pts = np.asarray(ax.collections[0].get_offsets())
    assert len(pts) == len(df), f"every row must be a point: expected {len(df)}, found {len(pts)}."


def test_no_confidence_band():
    ax = trend(make(4, 1.0)).axes[0]
    assert len(ax.collections) == 1, "ci=None: only the scatter collection should exist (no shaded band)."


def test_labels():
    ax = trend(make(5, 1.0)).axes[0]
    assert ax.get_xlabel() == "x" and ax.get_ylabel() == "y", "label the axes with the column names."
