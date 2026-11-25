import numpy as np
import pandas as pd
import pytest

from solution import fill_with_mean


def test_worked_example():
    filled, before, after = fill_with_mean(pd.Series([1, 2, 3, np.nan]))
    assert filled.tolist() == [1.0, 2.0, 3.0, 2.0], "the missing value is replaced by the mean of 1, 2, 3, which is 2.0."
    assert before == pytest.approx(1.0), "sd_before is the standard deviation of the observed values 1, 2, 3 (1.0)."
    assert after == pytest.approx(np.sqrt(2 / 3)), "sd_after is the standard deviation of [1, 2, 3, 2]: sqrt(2/3) = 0.8165."


def test_index_and_name_are_kept():
    s = pd.Series([4.0, np.nan, 8.0], index=["a", "b", "c"], name="income")
    filled, _, _ = fill_with_mean(s)
    assert filled.index.tolist() == ["a", "b", "c"] and filled.name == "income", "keep the index and the name."
    assert filled["b"] == pytest.approx(6.0)


def test_nothing_missing_changes_nothing():
    s = pd.Series([3.0, 5.0, 10.0])
    filled, before, after = fill_with_mean(s)
    assert filled.tolist() == [3.0, 5.0, 10.0]
    assert before == pytest.approx(after), "with nothing to fill, the two standard deviations are equal."


def test_spread_always_shrinks_when_something_is_filled():
    rng = np.random.default_rng(0)
    for _ in range(20):
        s = pd.Series(rng.normal(50, 10, 40))
        s[rng.random(40) < 0.3] = np.nan
        if s.isna().sum() == 0:
            continue
        _, before, after = fill_with_mean(s)
        assert after < before, "mean filling puts values exactly at the centre, so the standard deviation must shrink."


def test_input_not_changed_and_plain_floats():
    s = pd.Series([1.0, np.nan, 3.0])
    before_copy = s.copy()
    _, a, b = fill_with_mean(s)
    pd.testing.assert_series_equal(s, before_copy)
    assert type(a) is float and type(b) is float, "return plain floats (use float(...))."
