import numpy as np
import pandas as pd
import pytest

from solution import pooled_retention

IDX = ["2024-01", "2024-02", "2024-03"]
ACTIVE = pd.DataFrame({0: [100.0, 10.0, 50.0], 1: [50.0, 8.0, np.nan], 2: [30.0, np.nan, np.nan]}, index=IDX)
SIZES = pd.Series([100, 10, 50], index=IDX)


def test_weighted_and_mature_only():
    r = pooled_retention(ACTIVE, SIZES, [0, 1, 2])
    assert r[0] == pytest.approx(1.0), "month 0 is 1.0 for everyone."
    assert r[1] == pytest.approx(58 / 110), f"month 1: (50 + 8) / (100 + 10) = 0.527 (the March cohort has not reached it yet); got {r[1]:.3f}. The simple average of the rates would be 0.65."
    assert r[2] == pytest.approx(0.30), "month 2: only the January cohort has reached it: 30 / 100."


def test_unreached_or_missing_k_is_nan():
    r = pooled_retention(ACTIVE, SIZES, [3, 2])
    assert r.isna().tolist() == [True, False], "month 3 does not exist in the matrix: NaN."
    only_nan = pd.DataFrame({1: [np.nan, np.nan]}, index=["a", "b"])
    assert np.isnan(pooled_retention(only_nan, pd.Series([5, 6], index=["a", "b"]), [1])[1]), "no cohort reached it: NaN, not 0."


def test_series_indexed_by_ks_in_order():
    r = pooled_retention(ACTIVE, SIZES, [2, 0, 1])
    assert isinstance(r, pd.Series) and list(r.index) == [2, 0, 1], "a Series indexed by ks, in the order given."
    assert r.dtype == float
