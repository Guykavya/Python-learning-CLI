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

from solution import likert_bars

COLS = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]
COUNTS = pd.DataFrame([[10, 20, 20, 30, 20], [0, 0, 10, 30, 10]], index=["Q1", "Q2"], columns=COLS)


def patch(ax, c, q, n_questions=2):
    p = ax.patches[c * n_questions + q]
    return float(p.get_x()), float(p.get_width())


def test_structure_one_bar_per_category_and_question():
    ax = likert_bars(COUNTS).axes[0]
    assert len(ax.patches) == 10, f"5 categories x 2 questions = 10 bars (even zero-width ones), found {len(ax.patches)}."


def test_first_question_edges():
    ax = likert_bars(COUNTS).axes[0]
    expected = [(-40, 10), (-30, 20), (-10, 20), (10, 30), (40, 20)]
    for c, (left, width) in enumerate(expected):
        got = patch(ax, c, 0)
        assert got == pytest.approx((left, width)), f"Q1, {COLS[c]}: expected left={left}, width={width}, got {got}."


def test_zero_counts_draw_zero_width_bars():
    ax = likert_bars(COUNTS).axes[0]
    expected = [(-10, 0), (-10, 0), (-10, 20), (10, 60), (70, 20)]
    for c, (left, width) in enumerate(expected):
        got = patch(ax, c, 1)
        assert got == pytest.approx((left, width)), f"Q2, {COLS[c]}: expected left={left}, width={width}, got {got} (a 0% category is a zero-width bar, not a missing one)."


def test_neutral_is_centred_on_zero():
    ax = likert_bars(COUNTS).axes[0]
    for q in (0, 1):
        left, width = patch(ax, 2, q)
        assert left + width / 2 == pytest.approx(0.0), "the neutral bar must be centred on 0 (half of it on each side)."


def test_axis_label_zero_line_and_legend():
    ax = likert_bars(COUNTS).axes[0]
    assert ax.get_xlabel() == "Share of answers (%)", f"x label, got {ax.get_xlabel()!r}."
    assert any(set(ln.get_xdata()) == {0} for ln in ax.lines), "draw a vertical line at 0 (ax.axvline(0))."
    assert [t.get_text() for t in ax.get_legend().get_texts()] == COLS, "the legend lists the five categories in column order."


def test_question_labels():
    fig = likert_bars(COUNTS)
    fig.canvas.draw()
    assert [t.get_text() for t in fig.axes[0].get_yticklabels()] == ["Q1", "Q2"], "the y tick labels are the question names."
