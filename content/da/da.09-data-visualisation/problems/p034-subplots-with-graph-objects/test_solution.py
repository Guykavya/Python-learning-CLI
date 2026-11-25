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

from solution import two_panels

BARS = pd.DataFrame({"label": ["A", "B", "C"], "value": [150.0, 400.0, 220.0]})
TREND = pd.DataFrame({"month": [1, 2, 3, 4], "revenue": [10.0, 12.0, 11.0, 15.0]})


def test_two_traces_of_the_right_type():
    fig = two_panels(BARS, TREND)
    assert len(fig.data) == 2, f"one bar trace and one line trace, found {len(fig.data)}."
    assert fig.data[0].type == "bar" and fig.data[1].type == "scatter", "left panel go.Bar, right panel go.Scatter."
    assert fig.data[1].mode == "lines", "the right panel is a line (mode='lines')."


def test_traces_sit_in_their_panels():
    fig = two_panels(BARS, TREND)
    assert fig.data[0].xaxis == "x" and fig.data[1].xaxis == "x2", "add the second trace with col=2 so that it uses axis x2."


def test_data():
    fig = two_panels(BARS, TREND)
    assert list(fig.data[0].x) == ["A", "B", "C"] and [float(v) for v in fig.data[0].y] == [150.0, 400.0, 220.0], "left panel: label against value."
    assert [float(v) for v in fig.data[1].y] == [10.0, 12.0, 11.0, 15.0], "right panel: revenue by month."


def test_shared_y_axis_titled_once():
    fig = two_panels(BARS, TREND)
    assert fig.layout.yaxis.title.text == "Revenue (USD)", f"title the left y axis 'Revenue (USD)', got {fig.layout.yaxis.title.text!r}."
    assert fig.layout.yaxis2.title.text in (None, ""), "the shared y axis is titled once: leave the right one without a title."
    assert fig.layout.yaxis2.matches == "y", "the panels share the y axis (shared_yaxes=True)."


def test_title_and_legend():
    fig = two_panels(BARS, TREND)
    assert fig.layout.title.text == "Revenue overview", f"title, got {fig.layout.title.text!r}."
    assert fig.layout.showlegend is False, "turn the legend off (showlegend=False)."
    assert sorted(a.text for a in fig.layout.annotations) == ["By store", "Over time"], "give the panels their subplot titles."
