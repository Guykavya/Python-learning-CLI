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

from solution import heatmap

PIVOT = pd.DataFrame([[1.04, 2.5, np.nan], [4.0, 5.26, 6.0]], index=["Mon", "Tue"], columns=["am", "pm", "eve"])


def main_axes(fig):
    return [a for a in fig.axes if a.get_label() != "<colorbar>"][0]


def test_has_a_colorbar():
    fig = heatmap(PIVOT)
    assert len(fig.axes) == 2, f"the figure should have the heatmap Axes and a colour bar Axes (2), found {len(fig.axes)}."


def test_tick_labels():
    fig = heatmap(PIVOT)
    fig.canvas.draw()
    ax = main_axes(fig)
    assert [t.get_text() for t in ax.get_xticklabels()] == ["am", "pm", "eve"], "x tick labels are the column names."
    assert [t.get_text() for t in ax.get_yticklabels()] == ["Mon", "Tue"], "y tick labels are the row names."


def test_one_text_per_value_at_the_right_cell():
    ax = main_axes(heatmap(PIVOT))
    got = {tuple(t.get_position()): t.get_text() for t in ax.texts}
    expected = {(0, 0): "1.0", (1, 0): "2.5", (0, 1): "4.0", (1, 1): "5.3", (2, 1): "6.0"}
    assert got == expected, f"texts should be written at (column, row) with one decimal: expected {expected}, got {got}."


def test_nan_cell_has_no_text():
    ax = main_axes(heatmap(PIVOT))
    assert (2, 0) not in {tuple(t.get_position()) for t in ax.texts}, "the NaN cell (column 2, row 0) must have no text."
    assert all("nan" not in t.get_text().lower() for t in ax.texts), "never write 'nan' into a cell."


def test_image_holds_the_data():
    ax = main_axes(heatmap(PIVOT))
    arr = np.asarray(ax.images[0].get_array())
    assert arr.shape == (2, 3), f"the image should be 2 rows x 3 columns, got {arr.shape}."
    assert np.ma.getmaskarray(ax.images[0].get_array())[0, 2] or np.isnan(np.ma.filled(ax.images[0].get_array().astype(float), np.nan)[0, 2]), "the NaN cell stays blank."
