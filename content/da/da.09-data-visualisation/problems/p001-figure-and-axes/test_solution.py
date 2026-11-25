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

from matplotlib.figure import Figure
from solution import make_panels


def test_returns_a_figure():
    fig = make_panels(1, 1)
    assert fig is not None, "return fig: the function returned None (do not call plt.show())."
    assert isinstance(fig, Figure), "Return the Figure object, not the Axes."


@pytest.mark.parametrize("rows,cols", [(1, 1), (2, 3), (3, 1), (1, 4)])
def test_number_of_panels(rows, cols):
    fig = make_panels(rows, cols)
    assert len(fig.axes) == rows * cols, f"a {rows}x{cols} grid has {rows * cols} Axes, got {len(fig.axes)}."


def test_figsize_is_width_then_height():
    fig = make_panels(2, 2, figsize=(9, 5))
    w, h = fig.get_size_inches()
    assert (w, h) == (9, 5), f"figsize is (width, height) in inches; expected (9, 5), got ({w}, {h})."


def test_default_figsize():
    w, h = make_panels(1, 2).get_size_inches()
    assert (w, h) == (6, 4), "the default figsize is (6, 4)."


def test_shared_y_axis():
    fig = make_panels(2, 3, sharey=True)
    first = fig.axes[0]
    for other in fig.axes[1:]:
        assert first.get_shared_y_axes().joined(first, other), "with sharey=True every panel must share the y axis."


def test_independent_y_axes_by_default():
    fig = make_panels(1, 3)
    a, b, c = fig.axes
    assert not a.get_shared_y_axes().joined(a, b), "with sharey=False the panels must have independent y axes."
    assert not b.get_shared_y_axes().joined(b, c), "with sharey=False the panels must have independent y axes."
