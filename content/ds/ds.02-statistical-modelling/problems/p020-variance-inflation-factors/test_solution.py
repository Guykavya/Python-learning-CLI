import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from solution import vif_table


def make_df(seed, n=200):
    rng = np.random.default_rng(seed)
    x1 = rng.normal(5, 1, n)
    x2 = x1 + rng.normal(0, 0.03, n)        # almost a copy of x1
    x3 = rng.normal(10, 2, n)               # independent
    x4 = 0.5 * x3 + rng.normal(0, 1, n)     # moderately related to x3
    return pd.DataFrame({"x1": x1, "x2": x2, "x3": x3, "x4": x4})


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_statsmodels(seed):
    df = make_df(seed)
    cols = ["x1", "x2", "x3", "x4"]
    X = sm.add_constant(df[cols])
    ref = {c: variance_inflation_factor(X.to_numpy(), i) for i, c in enumerate(X.columns) if c != "const"}
    got = vif_table(df, cols)
    for c in cols:
        assert got[c] == pytest.approx(ref[c], rel=1e-6), f"VIF of {c} differs: regress it on the OTHER predictors WITH an intercept, then 1 / (1 - R2)."


def test_sorted_largest_first():
    got = vif_table(make_df(0), ["x1", "x2", "x3", "x4"])
    assert list(got.values) == sorted(got.values, reverse=True), "sort from the largest VIF to the smallest."
    assert set(got.index[:2]) == {"x1", "x2"}, "the near-duplicate pair must come first."


def test_near_duplicate_exceeds_ten_and_independent_is_near_one():
    df = make_df(1)
    got = vif_table(df, ["x1", "x2", "x3"])
    assert got["x1"] > 10 and got["x2"] > 10, "a column that is a copy of another has a huge VIF."
    assert got["x3"] < 1.3, "an independent predictor has a VIF near 1."


def test_single_predictor_has_vif_one():
    got = vif_table(make_df(0), ["x1"])
    assert got["x1"] == pytest.approx(1.0), "with no other predictor nothing inflates the variance: VIF = 1."
