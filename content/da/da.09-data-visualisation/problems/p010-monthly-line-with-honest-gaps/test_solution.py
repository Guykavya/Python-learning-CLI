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

from solution import monthly_line

DF = pd.DataFrame({
    "date": pd.to_datetime(["2024-01-05", "2024-01-20", "2024-02-10", "2024-04-02", "2024-04-30"]),
    "revenue": [100.0, 50.0, 80.0, 70.0, 30.0],
})


def line(fig):
    ln = fig.axes[0].lines[0]
    return pd.to_datetime(np.asarray(ln.get_xdata())), np.asarray(ln.get_ydata(), float)


def test_every_month_is_present():
    x, y = line(monthly_line(DF))
    assert len(x) == 4, f"the range Jan to Apr has 4 months, the line has {len(x)} points (add the missing month)."
    assert list(x.strftime("%Y-%m-%d")) == ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"], "x values are month START timestamps."


def test_sums_per_month_and_gap_is_nan():
    _, y = line(monthly_line(DF))
    assert y[0] == 150.0 and y[1] == 80.0 and y[3] == 100.0, f"monthly sums should be 150, 80, (gap), 100; got {list(y)}."
    assert np.isnan(y[2]), "March has no rows: its value must be NaN (a gap), not 0 and not interpolated."


def test_a_zero_month_is_not_a_gap():
    df = pd.DataFrame({"date": pd.to_datetime(["2024-01-05", "2024-02-05", "2024-03-05"]), "revenue": [10.0, 0.0, 5.0]})
    _, y = line(monthly_line(df))
    assert list(y) == [10.0, 0.0, 5.0], "a month with rows and revenue 0 is a real zero, not NaN."


def test_no_gap_data():
    df = pd.DataFrame({"date": pd.to_datetime(["2024-01-05", "2024-02-05"]), "revenue": [1.0, 2.0]})
    x, y = line(monthly_line(df))
    assert len(x) == 2 and not np.isnan(y).any(), "when no month is missing there must be no NaN."


def test_one_line_only():
    fig = monthly_line(DF)
    assert len(fig.axes[0].lines) == 1, "draw a single line (not one per month)."
