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

from matplotlib.cbook import boxplot_stats

from solution import box_stats


def test_hand_example():
    got = box_stats([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])
    assert got["q1"] == pytest.approx(3.25) and got["median"] == pytest.approx(5.5) and got["q3"] == pytest.approx(7.75), (
        f"quartiles should be 3.25, 5.5, 7.75 (np.percentile, linear), got {got['q1']}, {got['median']}, {got['q3']}.")
    assert got["whisker_high"] == 9.0, f"the upper whisker is the highest value INSIDE the fence (14.5), that is 9, got {got['whisker_high']}."
    assert got["whisker_low"] == 1.0
    assert got["outliers"] == [100.0], f"100 lies above the fence 14.5, got outliers {got['outliers']}."


def test_no_outliers():
    got = box_stats([4, 5, 6, 7, 8])
    assert got["outliers"] == [], "a compact sample has no outliers."
    assert got["whisker_low"] == 4.0 and got["whisker_high"] == 8.0, "without outliers the whiskers are the minimum and the maximum."


def test_low_and_high_outliers_are_sorted():
    got = box_stats([-50, 10, 11, 12, 13, 14, 15, 90, 60])
    assert got["outliers"] == sorted(got["outliers"]), "return the outliers sorted."
    assert -50.0 in got["outliers"] and 90.0 in got["outliers"], f"both tails can have outliers, got {got['outliers']}."


def test_value_on_the_fence_is_not_an_outlier():
    x = [0, 10, 10, 10, 10, 10, 10, 20]            # q1 = q3 = 10: fences are 10 and 10 -> 0 and 20 are outliers
    got = box_stats(x)
    assert got["outliers"] == [0.0, 20.0], f"values outside the fences are outliers, got {got['outliers']}."
    y = [1, 2, 3, 4, 5, 6, 7, 8]                    # q1 = 2.75, q3 = 6.25, fences -2.5 and 11.5 (no value on a fence)
    assert box_stats(y)["outliers"] == []


@pytest.mark.parametrize("seed", [0, 1, 2, 3])
def test_matches_matplotlib(seed):
    rng = np.random.default_rng(seed)
    x = np.concatenate([rng.normal(50, 10, 200), rng.normal(120, 5, 4)])
    got, ref = box_stats(x), boxplot_stats(x)[0]
    assert got["q1"] == pytest.approx(ref["q1"]) and got["median"] == pytest.approx(ref["med"]) and got["q3"] == pytest.approx(ref["q3"]), "quartiles differ from matplotlib's."
    assert got["whisker_low"] == pytest.approx(ref["whislo"]) and got["whisker_high"] == pytest.approx(ref["whishi"]), "whiskers end at the extreme values inside the fences."
    assert got["outliers"] == pytest.approx(sorted(ref["fliers"])), "outliers differ from matplotlib's fliers."


def test_plain_python_types():
    got = box_stats(np.array([1, 2, 3, 4, 50]))
    assert type(got["q1"]) is float and isinstance(got["outliers"], list), "return plain floats and a list."
