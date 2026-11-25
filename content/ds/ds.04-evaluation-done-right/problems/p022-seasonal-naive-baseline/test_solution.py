import numpy as np
import pytest

from conftest import make_sales
from solution import seasonal_naive


def test_worked_example():
    out = seasonal_naive(list(range(1, 15)), 10, 7)
    assert out.tolist() == [8, 9, 10, 11, 12, 13, 14, 8, 9, 10], "repeat the LAST full season (8..14)."
    assert out.dtype.kind == "f", "return floats."


def test_beats_the_mean_on_weekly_sales():
    s = make_sales()["sales"].to_numpy()
    train, test = s[:600], s[600:628]
    naive = seasonal_naive(train, 28, 7)
    assert np.mean(np.abs(test - naive)) < np.mean(np.abs(test - train.mean())), "on a trending weekly series, last week is a far better guess than the overall mean."


def test_formula_on_the_sales_series():
    s = make_sales(seed=1)["sales"].to_numpy()
    out = seasonal_naive(s[:500], 21, 7)
    expected = [s[500 - 7 + (i % 7)] for i in range(21)]
    assert out == pytest.approx(expected), "forecast[i] = train[len(train) - season + (i % season)]."


def test_too_short():
    with pytest.raises(ValueError):
        seasonal_naive([1.0, 2.0, 3.0], 5, 7)
