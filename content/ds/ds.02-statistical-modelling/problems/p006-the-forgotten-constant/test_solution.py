import numpy as np
import pandas as pd
import pytest

from solution import fit_ols


def make_df(seed=0, n=120):
    rng = np.random.default_rng(seed)
    x = rng.uniform(10, 20, n)           # far from zero, so a missing intercept is very costly
    z = rng.normal(size=n)
    y = 100 + 0.5 * x + 2.0 * z + rng.normal(0, 1.0, n)
    return pd.DataFrame({"y": y, "x": x, "z": z})


def test_has_an_intercept_column():
    res = fit_ols(make_df(), "y", ["x"])
    assert "const" in list(res.model.exog_names), "no constant in the design matrix: use sm.add_constant(df[xs]) before fitting."


def test_returns_a_results_object():
    res = fit_ols(make_df(), "y", ["x"])
    assert hasattr(res, "bse") and hasattr(res, "conf_int"), "return the fitted results object (the output of .fit()), not just the parameters."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_recovers_true_values(seed):
    res = fit_ols(make_df(seed), "y", ["x", "z"])
    lo, hi = res.conf_int().loc["const"]
    assert lo < 100 < hi, "the true intercept is 100 and should sit inside the 95% interval. Did you forget the constant?"
    lo, hi = res.conf_int().loc["x"]
    assert lo < 0.5 < hi, "the true slope for x is 0.5. Without an intercept this slope is badly biased."


def test_predictor_order_is_kept():
    res = fit_ols(make_df(), "y", ["z", "x"])
    assert list(res.model.exog_names) == ["const", "z", "x"], "keep the predictors in the order given, after the constant."
