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

from solution import overplot_scatter


def make(n, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({"x": rng.normal(size=n), "y": rng.normal(size=n)})


def points(fig):
    return fig.axes[0].collections[0]


@pytest.mark.parametrize("n", [100, 2000, 2500, 5000])
def test_every_point_is_drawn(n):
    fig = overplot_scatter(make(n), "X (cm)", "Y (kg)")
    assert len(points(fig).get_offsets()) == n, f"draw one marker per row: expected {n}, got {len(points(fig).get_offsets())} (do not sample)."


@pytest.mark.parametrize("n", [2001, 5000])
def test_large_sample_is_small_and_transparent(n):
    pts = points(overplot_scatter(make(n), "x", "y"))
    alpha = pts.get_alpha()
    assert alpha is not None and alpha <= 0.3, f"for n={n} use alpha <= 0.3 so dense areas look darker, got {alpha}."
    assert float(np.max(pts.get_sizes())) <= 10, f"for n={n} use small markers (s <= 10), got {np.max(pts.get_sizes())}."


@pytest.mark.parametrize("n", [50, 2000])
def test_small_sample_stays_visible(n):
    pts = points(overplot_scatter(make(n), "x", "y"))
    alpha = pts.get_alpha()
    assert alpha is None or alpha >= 0.5, f"for n={n} points are few: use alpha >= 0.5 (or none), got {alpha}."
    assert float(np.min(pts.get_sizes())) >= 20, f"for n={n} markers must be easy to see (s >= 20), got {np.min(pts.get_sizes())}."


def test_labels():
    ax = overplot_scatter(make(10), "Distance (km)", "Visits per month").axes[0]
    assert ax.get_xlabel() == "Distance (km)" and ax.get_ylabel() == "Visits per month", "set the x and y labels with their units."


def test_values_are_the_data():
    df = make(30, seed=3)
    pts = points(overplot_scatter(df, "x", "y"))
    off = np.asarray(pts.get_offsets())
    assert np.allclose(off[:, 0], df["x"]) and np.allclose(off[:, 1], df["y"]), "x and y must come from the columns x and y."
