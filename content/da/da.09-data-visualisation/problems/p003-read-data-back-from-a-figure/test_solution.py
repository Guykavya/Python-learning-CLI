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

from solution import bar_values, line_data


def test_vertical_bars():
    fig, ax = plt.subplots()
    ax.bar(["a", "b", "c"], [3, 1, 2])
    assert bar_values(ax) == [("a", 3.0), ("b", 1.0), ("c", 2.0)], "vertical bars: (x tick label, bar height) in drawing order."


def test_horizontal_bars_use_widths():
    fig, ax = plt.subplots()
    ax.barh(["x", "y", "z"], [5, 0, 2])
    assert bar_values(ax) == [("x", 5.0), ("y", 0.0), ("z", 2.0)], (
        "horizontal bars: the value is the bar WIDTH and the label is on the y axis (get_height() is only the thickness 0.8)."
    )


def test_zero_height_bar_is_kept():
    fig, ax = plt.subplots()
    ax.bar(["a", "b", "c"], [3, 0, 2])
    assert bar_values(ax) == [("a", 3.0), ("b", 0.0), ("c", 2.0)], "a bar of height 0 is still a bar: keep it in the list."


def test_equal_bars_are_vertical():
    fig, ax = plt.subplots()
    ax.bar(["a", "b", "c"], [2, 2, 2])
    assert bar_values(ax) == [("a", 2.0), ("b", 2.0), ("c", 2.0)], "when every bar is equal, treat the chart as vertical."


def test_values_are_plain_floats():
    fig, ax = plt.subplots()
    ax.bar(["a"], [4])
    label, value = bar_values(ax)[0]
    assert type(value) is float, "return Python floats: wrap the patch value with float(...)."


def test_no_bars():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    assert bar_values(ax) == [], "an Axes without bars gives an empty list."


def test_line_data():
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [5, 6, 7])
    ax.plot([0, 1, 2], [1, 1, 1])
    x, y = line_data(ax)
    assert list(x) == [0, 1, 2] and list(y) == [5.0, 6.0, 7.0], "line_data(ax) reads the first line by default."
    x2, y2 = line_data(ax, 1)
    assert list(y2) == [1.0, 1.0, 1.0], "line_data(ax, 1) reads the second line."
    assert isinstance(y, np.ndarray) and y.dtype == float, "return NumPy arrays, y with dtype float."


def test_line_data_keeps_nan():
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [1.0, np.nan, 3.0])
    _, y = line_data(ax)
    assert np.isnan(y[1]) and y[0] == 1.0 and y[2] == 3.0, "do not drop NaN: a gap in the data is information."
