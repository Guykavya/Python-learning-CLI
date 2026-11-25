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

from solution import alt_text


def vertical(names, values):
    fig, ax = plt.subplots()
    ax.bar(names, values)
    return fig


def horizontal(names, values):
    fig, ax = plt.subplots()
    ax.barh(names, values)
    return fig


def test_hand_example():
    fig = vertical(["Airport", "Mall", "Campus"], [4210, 2800, 1050])
    assert alt_text(fig, "revenue", "store") == "Bar chart of revenue by store. Highest: Airport (4,210). Lowest: Campus (1,050).", "exact format: see the example in the statement."


def test_horizontal_bars():
    fig = horizontal(["a", "b", "c"], [10, 2500, 7])
    assert alt_text(fig, "units", "category") == "Bar chart of units by category. Highest: b (2,500). Lowest: c (7).", "horizontal bars use the widths as values."


def test_ties_name_the_first_bar():
    fig = vertical(["x", "y", "z", "w"], [5, 9, 9, 5])
    assert alt_text(fig, "sales", "day") == "Bar chart of sales by day. Highest: y (9). Lowest: x (5).", "on ties, name the first bar in drawing order."


def test_single_bar():
    fig = vertical(["only"], [1234567])
    assert alt_text(fig, "revenue", "store") == "Bar chart of revenue by store. Highest: only (1,234,567). Lowest: only (1,234,567).", "one bar is both the highest and the lowest."


def test_values_are_rounded_to_whole_numbers():
    fig = vertical(["a", "b"], [1049.6, 2.4])
    assert alt_text(fig, "x", "y") == "Bar chart of x by y. Highest: a (1,050). Lowest: b (2).", "write values with a thousands separator and no decimals."
