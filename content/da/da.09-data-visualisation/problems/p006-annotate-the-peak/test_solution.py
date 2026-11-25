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

from solution import annotate_peak


def constant_lines(ax):
    return [ln for ln in ax.lines if len(set(np.asarray(ln.get_ydata(), float))) == 1]


def build(x, y):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    out = annotate_peak(ax, x, y)
    return ax, out


def test_one_annotation_pointing_at_the_peak():
    ax, _ = build([1, 2, 3, 4], [10, 40, 25, 5])
    assert len(ax.texts) == 1, f"add exactly one annotation, found {len(ax.texts)}."
    t = ax.texts[0]
    assert tuple(t.xy) == (2, 40), f"the annotation must point at the peak (2, 40), it points at {tuple(t.xy)}."


def test_text_is_formatted():
    ax, _ = build([1, 2, 3], [1000, 4210, 2500])
    assert ax.texts[0].get_text() == "Peak: 4,210", f"the text should be 'Peak: 4,210', got {ax.texts[0].get_text()!r}."


def test_mean_line():
    ax, _ = build([1, 2, 3, 4], [10, 40, 25, 5])
    lines = constant_lines(ax)
    assert len(lines) == 1, f"add exactly one horizontal line (ax.axhline); found {len(lines)} constant lines."
    assert float(lines[0].get_ydata()[0]) == pytest.approx(20.0), "the horizontal line belongs at the MEAN of y (20.0), not the median or the max."


def test_first_maximum_and_return_value():
    ax, out = build([5, 6, 7, 8], [3, 9, 9, 1])
    assert tuple(ax.texts[0].xy) == (6, 9), "when the maximum repeats, mark the first one."
    assert out is ax, "return the same Axes."


def test_data_line_untouched():
    ax, _ = build([1, 2, 3], [1, 5, 2])
    assert list(ax.lines[0].get_ydata()) == [1, 5, 2], "do not change the data line."
