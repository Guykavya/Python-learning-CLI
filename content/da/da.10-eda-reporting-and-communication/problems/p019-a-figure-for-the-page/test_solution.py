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

from solution import fig_contributions

SUMMARY = pd.DataFrame({"estimate": [1.37, 0.36, -0.59, 0.05, 0.21, 1.39], "CI low": [1.27, 0.18, -0.68, -0.35, 0.05, 1.09],
                        "CI high": [1.48, 0.55, -0.50, 0.43, 0.38, 1.73]},
                       index=["late deliveries", "price change", "customer mix", "September shift", "left unexplained", "observed rise (model)"])


def ax_of(summary=SUMMARY):
    fig = fig_contributions(summary)
    fig.canvas.draw()
    return fig.axes[0]


def test_one_bar_per_cause_sorted():
    ax = ax_of()
    labels = [t.get_text() for t in ax.get_yticklabels()]
    assert labels == ["customer mix", "September shift", "price change", "late deliveries"], f"drop the total rows and sort ascending (bottom to top), got {labels}"
    widths = [round(float(p.get_width()), 2) for p in ax.patches]
    assert widths == [-0.59, 0.05, 0.36, 1.37], f"bar lengths are the estimates, got {widths}"


def test_title_and_label():
    ax = ax_of()
    assert ax.get_title(loc="left") == "late deliveries explains 1.4 of the 1.4-point rise", f"title from the data, left-aligned; got {ax.get_title(loc='left')!r}"
    assert "percentage points" in ax.get_xlabel(), "the x label states the unit (percentage points)."


def test_error_bars_span_the_intervals():
    ax = ax_of()
    cont = [c for c in ax.containers if type(c).__name__ == "ErrorbarContainer"]
    assert cont, "draw the intervals with ax.errorbar."
    segs = cont[0].lines[2][0].get_segments()
    spans = [(round(float(s[0][0]), 2), round(float(s[1][0]), 2)) for s in segs]
    assert spans == [(-0.68, -0.5), (-0.35, 0.43), (0.18, 0.55), (1.27, 1.48)], f"each whisker runs from CI low to CI high, got {spans}"


def test_zero_line():
    ax = ax_of()
    assert any(set(np.asarray(l.get_xdata(), float)) == {0.0} for l in ax.lines), "draw a vertical line at 0 (ax.axvline(0))."


def test_title_follows_the_data():
    other = SUMMARY.copy()
    other.loc["price change", ["estimate", "CI low", "CI high"]] = [2.0, 1.8, 2.2]
    other.loc["observed rise (model)", "estimate"] = 2.5
    assert ax_of(other).get_title(loc="left") == "price change explains 2.0 of the 2.5-point rise", "the largest cause and the total come from the table."
