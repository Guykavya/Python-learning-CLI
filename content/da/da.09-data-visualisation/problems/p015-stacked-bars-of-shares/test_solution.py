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

from solution import share_bars

DF = pd.DataFrame({
    "store": ["B", "B", "A", "A", "B", "C"],
    "cat":   ["tea", "espresso", "tea", "espresso", "tea", "espresso"],
    "units": [10, 30, 30, 70, 10, 50],
})


def segments(ax):
    """{x position: [(bottom, height), ...]} in drawing order."""
    out = {}
    for p in ax.patches:
        out.setdefault(round(p.get_x() + p.get_width() / 2, 6), []).append((float(p.get_y()), float(p.get_height())))
    return out


def test_every_bar_adds_up_to_100():
    ax = share_bars(DF, "store", "cat", "units").axes[0]
    segs = segments(ax)
    assert len(segs) == 3, f"one bar per store: expected 3 bars, found {len(segs)}."
    for x, parts in segs.items():
        total = sum(h for _, h in parts)
        assert total == pytest.approx(100.0, abs=1e-9), f"the segments of one bar must add up to 100 (percent of the group total), got {total} at x={x}."


def test_shares_are_correct():
    ax = share_bars(DF, "store", "cat", "units").axes[0]
    ax.figure.canvas.draw()
    labels = [t.get_text() for t in ax.get_xticklabels()]
    assert labels == ["B", "A", "C"], f"groups keep their first-appearance order B, A, C, got {labels}."
    by_part = {c.get_label(): [float(q.get_height()) for q in c] for c in ax.containers}
    assert by_part["tea"] == pytest.approx([40.0, 30.0, 0.0]), f"tea share per store (B: 20 of 50 = 40%, A: 30%, C: 0%), got {by_part['tea']}."
    assert by_part["espresso"] == pytest.approx([60.0, 70.0, 100.0]), f"espresso share per store (60, 70, 100), got {by_part['espresso']}."


def test_missing_part_is_a_zero_segment():
    ax = share_bars(DF, "store", "cat", "units").axes[0]
    assert len(ax.patches) == 6, f"3 groups x 2 parts = 6 segments (a missing part is a zero-height segment), found {len(ax.patches)}."


def test_stacking_uses_bottom():
    ax = share_bars(DF, "store", "cat", "units").axes[0]
    first, second = ax.containers
    assert all(float(p.get_y()) == 0.0 for p in first), "the first part starts at 0."
    for lower, upper in zip(first, second):
        assert float(upper.get_y()) == pytest.approx(float(lower.get_height())), "the second part must start where the first one ends (use bottom=)."


def test_legend_order_matches_the_stack():
    ax = share_bars(DF, "store", "cat", "units").axes[0]
    texts = [t.get_text() for t in ax.get_legend().get_texts()]
    assert texts == ["tea", "espresso"], f"legend entries must follow the stack from the bottom: ['tea', 'espresso'], got {texts}."
