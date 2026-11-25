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

from solution import bubble_chart, bubble_sizes


def test_hand_example():
    assert list(bubble_sizes([10, 20, 40], 400)) == pytest.approx([100.0, 200.0, 400.0]), "area = max_area * value / max(value): [100, 200, 400]."


def test_doubling_a_value_doubles_the_area():
    s = bubble_sizes([3, 6, 12, 5], 900)
    assert s[1] == pytest.approx(2 * s[0]) and s[2] == pytest.approx(2 * s[1]), "area must be proportional to the value (not to the radius)."


def test_largest_gets_max_area_and_zero_stays_zero():
    s = bubble_sizes([0, 5, 25], 300)
    assert s.max() == pytest.approx(300.0) and s[0] == 0.0, "the largest value gets max_area; a zero value gets area 0."


def test_negative_and_all_zero():
    with pytest.raises(ValueError, match="negative value"):
        bubble_sizes([1, -2], 100)
    assert list(bubble_sizes([0, 0, 0], 100)) == [0.0, 0.0, 0.0], "all zeros: no division by zero, return zeros."


def test_returns_a_numpy_array():
    assert isinstance(bubble_sizes([1, 2], 10), np.ndarray), "return a NumPy array."


def test_chart_uses_the_sizes():
    fig = bubble_chart([1, 2, 3], [4, 5, 6], [10, 20, 40], max_area=400)
    pts = fig.axes[0].collections[0]
    assert list(pts.get_sizes()) == pytest.approx([100.0, 200.0, 400.0]), "pass the areas to ax.scatter(s=...)."
    assert len(pts.get_offsets()) == 3, "one bubble per row."
