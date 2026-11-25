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


def make(first, last, n=24):
    return pd.DataFrame({"date": pd.date_range("2023-01-01", periods=n, freq="MS"),
                         "revenue": np.linspace(first, last, n)})


def points(ax):
    if ax.lines:
        return len(ax.lines[0].get_xdata())
    return len(ax.patches)


def test_all_months_are_drawn():
    df = make(100000, 125000)
    ax = revenue_chart(df).axes[0]
    assert points(ax) == 24, f"draw every month (24), not a cherry-picked window; the chart shows {points(ax)}."


def test_axis_starts_at_zero():
    ax = revenue_chart(make(100000, 125000)).axes[0]
    assert ax.get_ylim()[0] == 0, f"the value axis must start at 0, it starts at {ax.get_ylim()[0]:g}."


def test_unit_on_the_y_label():
    ax = revenue_chart(make(100000, 125000)).axes[0]
    assert "USD" in ax.get_ylabel(), f"say the unit on the y axis (USD), the label is {ax.get_ylabel()!r}."


def test_title_states_the_growth():
    ax = revenue_chart(make(100000, 125000)).axes[0]
    assert ax.get_title() == "Revenue grew 25% from Jan 2023 to Dec 2024", f"the title should state the change in numbers, got {ax.get_title()!r}."


def test_title_follows_the_data():
    ax = revenue_chart(make(100000, 80000)).axes[0]
    assert ax.get_title() == "Revenue fell 20% from Jan 2023 to Dec 2024", f"for falling revenue the title must say 'fell' and the right number, got {ax.get_title()!r}. Do not type the number: compute it."


def test_short_series():
    df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-02-01"]), "revenue": [200.0, 200.0]})
    ax = revenue_chart(df).axes[0]
    assert ax.get_title() == "Revenue grew 0% from Jan 2024 to Feb 2024", f"equal first and last month count as 'grew 0%', got {ax.get_title()!r}."
