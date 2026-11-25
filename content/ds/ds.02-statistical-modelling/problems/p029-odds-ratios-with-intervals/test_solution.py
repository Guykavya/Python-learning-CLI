import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
import statsmodels.formula.api as smf

from solution import odds_ratios


def fit_arrays(seed, n=600):
    rng = np.random.default_rng(seed)
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    p = 1 / (1 + np.exp(-(-0.3 + 1.2 * x1 + 0.0 * x2)))
    y = (rng.random(n) < p).astype(int)
    return sm.Logit(y, sm.add_constant(np.column_stack([x1, x2]))).fit(disp=0)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_values_match_exp_of_log_odds(seed):
    res = fit_arrays(seed)
    out = odds_ratios(res)
    ci = np.asarray(res.conf_int())
    assert list(out.columns) == ["odds_ratio", "ci_low", "ci_high", "p"], "columns: odds_ratio, ci_low, ci_high, p, in that order."
    assert out["odds_ratio"].to_numpy() == pytest.approx(np.round(np.exp(res.params), 3)), "odds_ratio = exp(coefficient), rounded after the exp."
    assert out["ci_low"].to_numpy() == pytest.approx(np.round(np.exp(ci[:, 0]), 3)), "ci_low = exp(lower end of the log-odds interval)."
    assert out["ci_high"].to_numpy() == pytest.approx(np.round(np.exp(ci[:, 1]), 3)), "ci_high = exp(upper end of the log-odds interval)."
    assert out["p"].to_numpy() == pytest.approx(np.round(res.pvalues, 3)), "p-values are not exponentiated."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_a_real_effect_has_an_interval_above_one(seed):
    out = odds_ratios(fit_arrays(seed))
    assert out.loc["x1", "ci_low"] > 1.0, "x1 has a true odds ratio exp(1.2) = 3.3: its whole interval should lie above 1."
    assert 2.0 < out.loc["x1", "odds_ratio"] < 5.5, "the estimated odds ratio of x1 should be near 3.3."


def test_index_names_for_formula_models():
    rng = np.random.default_rng(8)
    df = pd.DataFrame({"x": rng.normal(size=400)})
    df["y"] = (rng.random(400) < 1 / (1 + np.exp(-0.8 * df["x"]))).astype(int)
    out = odds_ratios(smf.logit("y ~ x", data=df).fit(disp=0))
    assert list(out.index) == ["Intercept", "x"], "index = parameter names in model order."


def test_interval_contains_the_estimate():
    out = odds_ratios(fit_arrays(4))
    assert ((out["ci_low"] <= out["odds_ratio"]) & (out["odds_ratio"] <= out["ci_high"])).all(), "the interval must contain its own estimate."
