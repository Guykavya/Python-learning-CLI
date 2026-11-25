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

from scipy import stats

from solution import means_with_ci


def make():
    rng = np.random.default_rng(1)
    return pd.DataFrame({
        "loyal": ["yes"] * 40 + ["no"] * 60,
        "ticket": np.concatenate([rng.normal(7.0, 1.2, 40), rng.normal(6.4, 1.5, 60)]),
    })


def expected(df):
    out = {}
    for name, g in df.groupby("loyal"):
        x = g["ticket"].to_numpy()
        se = x.std(ddof=1) / np.sqrt(len(x))
        out[name] = (x.mean(), stats.t.ppf(0.975, len(x) - 1) * se)
    return out


def drawn(fig):
    cont = fig.axes[0].containers[0]
    means = np.asarray(cont.lines[0].get_ydata(), float)
    segs = cont.lines[2][0].get_segments()
    halves = np.array([(s[1][1] - s[0][1]) / 2 for s in segs])
    return means, halves


def test_uses_errorbar():
    fig = means_with_ci(make(), "loyal", "ticket")
    assert type(fig.axes[0].containers[0]).__name__ == "ErrorbarContainer", "draw the points with ax.errorbar (not ax.bar(yerr=...))."


def test_means_and_half_lengths():
    df = make()
    fig = means_with_ci(df, "loyal", "ticket")
    means, halves = drawn(fig)
    exp = expected(df)                                     # sorted groups: no, yes
    assert means == pytest.approx([exp["no"][0], exp["yes"][0]]), f"the dots must sit at each group's mean (groups sorted), got {means}."
    assert halves == pytest.approx([exp["no"][1], exp["yes"][1]]), f"the whisker half-lengths must equal the 95% t half-widths, got {halves}."


def test_group_order_and_labels():
    fig = means_with_ci(make(), "loyal", "ticket")
    fig.canvas.draw()
    assert [t.get_text() for t in fig.axes[0].get_xticklabels()] == ["no", "yes"], "groups appear in sorted order."


def test_axis_and_title():
    ax = means_with_ci(make(), "loyal", "ticket").axes[0]
    assert ax.get_ylim()[0] == 0, f"the y axis must start at 0, it starts at {ax.get_ylim()[0]:g}."
    assert "95% CI" in ax.get_title(), f"say what the whiskers are: the title must contain '95% CI', got {ax.get_title()!r}."
    assert ax.get_ylabel() == "ticket", "the y label is the name of the value column."


def test_other_data():
    df = pd.DataFrame({"g": ["a"] * 4 + ["b"] * 4, "v": [8, 10, 12, 10, 1, 2, 3, 2.0]})
    means, halves = drawn(means_with_ci(df, "g", "v"))
    assert means == pytest.approx([10.0, 2.0]), "means of the toy data are 10 and 2."
    assert halves[0] > halves[1], "the group with the larger spread has the wider interval."
