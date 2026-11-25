import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

from solution import diagnose


def make(seed, n=120):
    rng = np.random.default_rng(seed)
    x1 = rng.normal(5, 1, n)
    x2 = 0.8 * x1 + rng.normal(0, 0.6, n)
    x3 = rng.normal(20, 4, n)
    y = 3 + x1 - 0.5 * x2 + 0.2 * x3 + np.cumsum(rng.normal(0, 0.3, n))   # a drifting error: Durbin-Watson well below 2
    return pd.DataFrame({"y": y, "x1": x1, "x2": x2, "x3": x3})


@pytest.fixture(params=[0, 1, 2])
def res(request):
    df = make(request.param)
    return sm.OLS(df["y"], sm.add_constant(df[["x1", "x2", "x3"]])).fit()


def test_keys(res):
    assert set(diagnose(res)) == {"r2", "bp_p", "dw", "n_high_leverage", "n_cooks_flagged", "max_vif"}, "keep exactly the six documented keys."


def test_r2(res):
    assert diagnose(res)["r2"] == pytest.approx(res.rsquared), "r2 is result.rsquared."


def test_durbin_watson_uses_residuals(res):
    assert diagnose(res)["dw"] == pytest.approx(sm.stats.durbin_watson(res.resid)), "dw: Durbin-Watson is computed from the RESIDUALS, not from the fitted values."


def test_leverage_threshold(res):
    n, p = int(res.nobs), len(res.params)
    expected = int(np.sum(res.get_influence().hat_matrix_diag > 2 * p / n))
    assert diagnose(res)["n_high_leverage"] == expected, "n_high_leverage: the rule of thumb is h > 2p/n, not p/n."


def test_cooks_count(res):
    n = int(res.nobs)
    expected = int(np.sum(res.get_influence().cooks_distance[0] > 4 / n))
    assert diagnose(res)["n_cooks_flagged"] == expected, "n_cooks_flagged: count rows with D > 4/n."


def test_max_vif_skips_the_constant(res):
    exog = res.model.exog
    expected = max(variance_inflation_factor(exog, i) for i in range(1, exog.shape[1]))
    assert diagnose(res)["max_vif"] == pytest.approx(expected, rel=1e-8), "max_vif: the constant column is not a predictor; leave it out of the loop."


def test_works_with_formula_models_too():
    df = make(5)
    r = smf.ols("y ~ x1 + x2 + x3", data=df).fit()
    exog = r.model.exog
    expected = max(variance_inflation_factor(exog, i) for i in range(1, exog.shape[1]))
    assert diagnose(r)["max_vif"] == pytest.approx(expected, rel=1e-8), "formula models call the constant 'Intercept': skip that name as well."
