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

from solution import revenue_chart

DF = pd.DataFrame({"month": pd.date_range("2024-01-01", periods=6, freq="MS"),
                   "revenue": [8000, 9500, 12000, 11000, 15000, 14000]})


def test_linear_axis_starts_at_zero():
    ax = revenue_chart(DF).axes[0]
    assert ax.get_yscale() == "linear", "log=False must keep a linear y scale."
    assert ax.get_ylim()[0] == 0, f"the linear y axis must start at 0, it starts at {ax.get_ylim()[0]:g}."


def test_log_axis():
    ax = revenue_chart(DF, log=True).axes[0]
    assert ax.get_yscale() == "log", "log=True must give a logarithmic y scale (ax.set_yscale('log'))."
    assert ax.get_ylim()[0] > 0, "a log axis cannot include 0: do not force bottom=0 there."


@pytest.mark.parametrize("log", [False, True])
def test_thousands_separator(log):
    ax = revenue_chart(DF, log=log).axes[0]
    fmt = ax.yaxis.get_major_formatter()
    assert fmt(12000, 0) == "12,000", f"a tick at 12000 should read '12,000', got {fmt(12000, 0)!r} (use FuncFormatter with {{v:,.0f}})."
    assert fmt(1500000, 0) == "1,500,000", "the separator must work for millions too."


def test_label_and_data():
    ax = revenue_chart(DF).axes[0]
    assert ax.get_ylabel() == "Revenue (USD)", f"label the y axis with its unit: 'Revenue (USD)', got {ax.get_ylabel()!r}."
    assert list(ax.lines[0].get_ydata()) == list(DF["revenue"]), "the line must draw the revenue column."
