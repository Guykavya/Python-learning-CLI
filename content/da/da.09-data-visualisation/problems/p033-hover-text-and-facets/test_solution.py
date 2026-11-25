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

from solution import px_lines

DF = pd.DataFrame({
    "month": [1, 2, 3, 1, 2, 3],
    "store": ["A", "A", "A", "B", "B", "B"],
    "revenue": [10.0, 12.0, 14.0, 20.0, 22.0, 24.0],
    "units": [3, 4, 5, 6, 7, 8],
})


def test_one_trace_per_store():
    fig = px_lines(DF)
    assert len(fig.data) == 2, f"one trace per store (facet_col='store'): expected 2, found {len(fig.data)}."
    assert [t.xaxis for t in fig.data] == ["x", "x2"], "the second store lives in its own panel (axis x2)."


def test_units_are_in_the_tooltip_in_row_order():
    fig = px_lines(DF)
    for trace, expected in zip(fig.data, ([3, 4, 5], [6, 7, 8])):
        assert trace.customdata is not None, "hover_data=['units'] stores the extra column in customdata."
        assert np.asarray(trace.customdata)[:, 0].tolist() == expected, f"customdata[0] should hold the units {expected}."


def test_hovertemplate_mentions_unit_and_units_column():
    tpl = px_lines(DF).data[0].hovertemplate
    assert "Revenue (USD)" in tpl, f"the tooltip must name the unit 'Revenue (USD)' (labels=...), template: {tpl!r}."
    assert "customdata[0]" in tpl, "the tooltip must show the extra column units."


def test_title_and_panel_names():
    fig = px_lines(DF)
    assert fig.layout.title.text == "Revenue by month", f"title, got {fig.layout.title.text!r}."
    assert sorted(a.text for a in fig.layout.annotations) == ["store=A", "store=B"], "one facet title per store."


def test_data_values():
    fig = px_lines(DF)
    assert [float(v) for v in fig.data[1].y] == [20.0, 22.0, 24.0], "the second trace is store B's revenue."
