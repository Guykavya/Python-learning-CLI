import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
import statsmodels.formula.api as smf

from solution import coef_report


@pytest.fixture
def ols_res():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"x": rng.normal(size=80), "z": rng.normal(size=80)})
    df["y"] = 1 + 2 * df.x - 0.5 * df.z + rng.normal(size=80)
    return smf.ols("y ~ x + z", data=df).fit()


@pytest.fixture
def logit_res():
    rng = np.random.default_rng(1)
    x = rng.normal(size=300)
    p = 1 / (1 + np.exp(-(0.3 + 1.2 * x)))
    y = (rng.random(300) < p).astype(int)
    return sm.Logit(y, sm.add_constant(x)).fit(disp=0)


def test_columns_and_index(ols_res):
    t = coef_report(ols_res)
    assert list(t.columns) == ["estimate", "ci_low", "ci_high", "p"], "columns must be exactly estimate, ci_low, ci_high, p in that order."
    assert list(t.index) == ["Intercept", "x", "z"], "the index is the parameter names in the model's order."


def test_values_match_statsmodels(ols_res):
    t = coef_report(ols_res, digits=6)
    ci = ols_res.conf_int()
    assert t["estimate"].to_numpy() == pytest.approx(ols_res.params.to_numpy(), abs=1e-6), "estimate column should be result.params."
    assert t["ci_low"].to_numpy() == pytest.approx(ci[0].to_numpy(), abs=1e-6), "ci_low is the first column of conf_int()."
    assert t["ci_high"].to_numpy() == pytest.approx(ci[1].to_numpy(), abs=1e-6), "ci_high is the second column of conf_int()."
    assert t["p"].to_numpy() == pytest.approx(ols_res.pvalues.to_numpy(), abs=1e-6), "p is result.pvalues."


def test_rounding_default_is_three_digits(ols_res):
    t = coef_report(ols_res)
    assert np.allclose(t.to_numpy(), np.round(t.to_numpy(), 3)), "round every number to `digits` (default 3) decimals."


def test_works_on_array_models(logit_res):
    t = coef_report(logit_res)
    assert t.shape == (2, 4), "also works when the model was fitted on plain arrays (conf_int() is then an ndarray)."
    assert list(t.index) == ["const", "x1"], "array models name parameters const, x1, x2, ... (use result.model.exog_names)."


def test_exponentiate_gives_odds_ratios(logit_res):
    raw = coef_report(logit_res, digits=8)
    odds = coef_report(logit_res, exponentiate=True, digits=8)
    for col in ["estimate", "ci_low", "ci_high"]:
        assert odds[col].to_numpy() == pytest.approx(np.exp(raw[col].to_numpy()), rel=1e-6), f"{col} must be exp(...) when exponentiate=True."
    assert odds["p"].to_numpy() == pytest.approx(raw["p"].to_numpy()), "never exponentiate the p-value."
    assert (odds["ci_low"] <= odds["estimate"]).all() and (odds["estimate"] <= odds["ci_high"]).all(), "the interval must still contain the estimate after exp()."
