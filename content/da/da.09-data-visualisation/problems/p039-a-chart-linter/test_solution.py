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

from solution import lint_figure


def good():
    fig, ax = plt.subplots()
    ax.bar(["a", "b", "c"], [3, 5, 2])
    ax.set_title("Revenue by store")
    ax.set_ylabel("Revenue (USD)")
    return fig


def test_good_figure_has_no_problems():
    assert lint_figure(good()) == [], "a titled, labelled bar chart from zero with default fonts has no problems."


def test_missing_title():
    fig, ax = plt.subplots()
    ax.plot([1, 2], [1, 2])
    ax.set_xlabel("x"); ax.set_ylabel("y")
    assert lint_figure(fig) == ["axes[0]: no title"], "exactly one problem: no title."


def test_missing_labels():
    fig, ax = plt.subplots()
    ax.plot([1, 2], [1, 2])
    ax.set_title("t")
    assert lint_figure(fig) == ["axes[0]: no axis labels"], "an Axes with data and no x or y label is flagged."


def test_truncated_vertical_and_horizontal_bars():
    fig, ax = plt.subplots()
    ax.bar(["2023", "2024"], [2.108, 2.344])
    ax.set_ylim(2.0, 2.4)
    ax.set_title("t"); ax.set_ylabel("y")
    assert lint_figure(fig) == ["axes[0]: bar chart value axis starts at 2, not 0"], "vertical bars: the y axis must include 0."
    fig2, ax2 = plt.subplots()
    ax2.barh(["a", "b", "c"], [50, 60, 55])
    ax2.set_xlim(40, 65)
    ax2.set_title("t"); ax2.set_xlabel("x")
    assert lint_figure(fig2) == ["axes[0]: bar chart value axis starts at 40, not 0"], "horizontal bars: the x axis must include 0."


def test_too_many_legend_entries_and_limit_argument():
    fig, ax = plt.subplots()
    for k in range(9):
        ax.plot([0, 1], [k, k + 1], label=f"s{k}")
    ax.legend()
    ax.set_title("t"); ax.set_xlabel("x")
    assert lint_figure(fig) == ["axes[0]: legend has 9 entries (more than 7)"], "nine legend entries is too many: use small multiples."
    assert lint_figure(fig, max_legend=9) == [], "the limit is a parameter."


def test_small_text_once_per_figure():
    fig = good()
    fig.axes[0].text(0, 1, "note", fontsize=5)
    fig.axes[0].text(1, 1, "note2", fontsize=6)
    assert lint_figure(fig) == ["text smaller than 8 pt"], "report small text once, not once per text."
    assert lint_figure(good(), min_font=11) == ["text smaller than 11 pt"], "min_font is a parameter: default tick labels are 10 pt."


def test_several_axes_and_colorbar():
    fig, axes = plt.subplots(1, 2)
    axes[0].plot([1, 2], [1, 2]); axes[0].set_title("a"); axes[0].set_xlabel("x")
    axes[1].plot([1, 2], [2, 1]); axes[1].set_xlabel("x")
    assert lint_figure(fig) == ["axes[1]: no title"], "name the Axes by its index in fig.axes."
    fig2, ax = plt.subplots()
    im = ax.imshow(np.arange(4.0).reshape(2, 2))
    fig2.colorbar(im, ax=ax)
    ax.set_title("heat")
    assert lint_figure(fig2) == [], "skip the colour-bar Axes and do not ask labels of an image."


def test_messages_come_in_order():
    fig, ax = plt.subplots()
    ax.bar(["a", "b"], [2.1, 2.3])
    ax.set_ylim(2.0, 2.4)
    ax.text(0, 2.35, "tiny", fontsize=5)
    assert lint_figure(fig) == ["axes[0]: no title", "axes[0]: no axis labels", "axes[0]: bar chart value axis starts at 2, not 0", "text smaller than 8 pt"], (
        "order: title, labels, bars, legend for each Axes, then the font check.")
