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

import matplotlib.colors

from solution import direct_label


def build(with_legend=True):
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [1, 2, 3], color="#d55e00", label="Airport")
    ax.plot([0, 1, 2], [2, 2, 2], color="#0072b2", label="Campus")
    ax.plot([0, 1, 2], [5, 4, 1], color="#009e73", label="Mall")
    ax.axhline(2.5, color="grey")                       # an unlabelled reference line
    if with_legend:
        ax.legend()
    return ax


def test_legend_is_removed():
    ax = direct_label(build())
    assert ax.get_legend() is None, "direct labels replace the legend: remove it."


def test_one_text_per_labelled_line_at_its_last_point():
    ax = direct_label(build())
    got = {t.get_text(): tuple(float(v) for v in t.get_position()) for t in ax.texts}
    assert got == {"Airport": (2.0, 3.0), "Campus": (2.0, 2.0), "Mall": (2.0, 1.0)}, f"write each name at the last point of its line, got {got}."


def test_text_colour_follows_the_line():
    ax = direct_label(build())
    colours = {t.get_text(): matplotlib.colors.to_hex(t.get_color()) for t in ax.texts}
    assert colours == {"Airport": "#d55e00", "Campus": "#0072b2", "Mall": "#009e73"}, f"the text colour must equal the line colour, got {colours}."


def test_reference_line_is_not_labelled():
    ax = direct_label(build())
    assert len(ax.texts) == 3, f"the unlabelled axhline gets no text; found {len(ax.texts)} texts."


def test_works_without_a_legend_and_returns_ax():
    ax = build(with_legend=False)
    assert direct_label(ax) is ax, "return the same Axes."
    assert ax.get_legend() is None, "without a legend there is still none afterwards (do not create one)."
