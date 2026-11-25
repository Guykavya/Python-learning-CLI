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

import matplotlib as mpl

from solution import themed_chart

DF = pd.DataFrame({"label": ["a", "b", "c"], "value": [3, 5, 2]})


@pytest.fixture(autouse=True)
def _restore_rcparams():
    before = dict(mpl.rcParams)
    yield
    mpl.rcParams.update(before)


def test_rcparams_are_unchanged_afterwards():
    before = dict(mpl.rcParams)
    themed_chart(DF)
    changed = sorted(k for k in before if mpl.rcParams[k] != before[k])
    assert not changed, f"sns.set_theme() changes every later chart in the program. Use `with sns.axes_style(...)`; changed keys: {changed[:5]}."


def test_calling_twice_leaves_a_plain_chart_plain():
    themed_chart(DF)
    themed_chart(DF)
    fig, ax = plt.subplots()
    ax.plot([1, 2], [1, 2])
    assert not ax.yaxis.get_gridlines()[0].get_visible(), "a chart drawn later must not inherit the whitegrid style."
    assert ax.title.get_fontsize() == pytest.approx(mpl.rcParamsDefault["axes.titlesize"] if isinstance(mpl.rcParamsDefault["axes.titlesize"], (int, float)) else 12.0), "a later chart must keep the default font size."


def test_the_chart_itself_has_the_style():
    ax = themed_chart(DF).axes[0]
    assert ax.yaxis.get_gridlines()[0].get_visible(), "inside the block the whitegrid style shows the y grid."
    assert ax.title.get_fontsize() > 14, f"the talk context makes text larger than the default; the title is {ax.title.get_fontsize()} pt."
    assert ax.get_title() == "Value by label", f"the title should be 'Value by label', got {ax.get_title()!r}."


def test_bars():
    ax = themed_chart(DF).axes[0]
    assert [float(p.get_height()) for p in ax.patches] == [3.0, 5.0, 2.0], "draw the value column as bar heights."
