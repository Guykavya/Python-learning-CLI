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

from solution import px_bars

DF = pd.DataFrame({"store": ["A", "A", "B", "C", "B"], "revenue": [100.0, 50.0, 300.0, 220.0, 100.0]})


def test_values_and_order():
    fig = px_bars(DF)
    assert list(fig.data[0].y) == ["A", "C", "B"], f"order the stores ascending, A, C, B (plotly draws the first at the bottom), got {list(fig.data[0].y)}."
    assert [float(v) for v in fig.data[0].x] == [150.0, 220.0, 400.0], "bar lengths are the revenue totals 150, 220, 400."


def test_horizontal():
    fig = px_bars(DF)
    assert fig.data[0].orientation == "h", "use orientation='h' for horizontal bars."


def test_title_and_axis_titles():
    fig = px_bars(DF)
    assert fig.layout.title.text == "Revenue by store", f"title, got {fig.layout.title.text!r}."
    assert fig.layout.xaxis.title.text == "Revenue (USD)", f"x axis title, got {fig.layout.xaxis.title.text!r}."
    assert fig.layout.yaxis.title.text == "Store", f"y axis title, got {fig.layout.yaxis.title.text!r}."


def test_one_trace_only():
    assert len(px_bars(DF).data) == 1, "one trace of bars."
