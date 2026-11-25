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

from solution import hist_by_group


def make():
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "value": np.concatenate([rng.normal(0, 1, 300), rng.normal(3, 1, 100)]),
        "group": ["a"] * 300 + ["b"] * 100,
    })


def areas(ax):
    out = {}
    for p in ax.patches:
        key = tuple(np.round(p.get_facecolor(), 3))
        out[key] = out.get(key, 0.0) + float(p.get_width() * p.get_height())
    return list(out.values())


def test_each_group_has_area_one():
    ax = hist_by_group(make()).axes[0]
    a = areas(ax)
    assert len(a) == 2, f"two groups should give two colours of bars, found {len(a)}."
    for total in a:
        assert total == pytest.approx(1.0, abs=0.01), (
            f"each group's bars should have total area 1 (stat='density', common_norm=False); got areas {[round(v, 3) for v in a]}.")


def test_legend_lists_the_groups():
    ax = hist_by_group(make()).axes[0]
    legend = ax.get_legend()
    assert legend is not None, "split by group with hue=, so seaborn adds a legend."
    assert sorted(t.get_text() for t in legend.get_texts()) == ["a", "b"], "the legend entries are the group names."


def test_returns_a_figure_with_one_axes():
    fig = hist_by_group(make())
    assert len(fig.axes) == 1, f"draw on one Axes; found {len(fig.axes)} (pass ax=ax to seaborn)."


def test_three_groups():
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"value": rng.normal(size=300), "group": ["x"] * 200 + ["y"] * 70 + ["z"] * 30})
    a = areas(hist_by_group(df).axes[0])
    assert len(a) == 3 and all(abs(t - 1) < 0.01 for t in a), f"every group's area must be 1, got {[round(v, 3) for v in a]}."
