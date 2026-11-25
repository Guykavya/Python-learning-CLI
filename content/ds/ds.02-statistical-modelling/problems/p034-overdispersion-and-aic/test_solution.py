import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

from solution import choose_count_model, lr_test


def make(n, seed, over):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=n)
    mu = np.exp(0.5 + 0.4 * x)
    y = rng.poisson(mu * rng.gamma(1.5, 1 / 1.5, n)) if over else rng.poisson(mu)
    return pd.DataFrame({"y": y, "x": x})


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_overdispersed_counts_choose_negbin(seed):
    out = choose_count_model(make(800, seed, True))
    assert out["dispersion"] > 1.5, f"dispersion {out['dispersion']:.2f}: for gamma-mixed counts the Pearson ratio is about 2. Use pearson_chi2 / df_resid of the Poisson GLM."
    assert out["best"] == "negbin", "with real overdispersion the negative binomial has the clearly lower AIC."
    assert out["aic_negbin"] < out["aic_poisson"] - 50, "the AIC gap should be large here."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_poisson_counts_keep_poisson(seed):
    out = choose_count_model(make(800, seed, False))
    assert 0.8 < out["dispersion"] < 1.3, f"dispersion {out['dispersion']:.2f}: true Poisson counts give a ratio near 1."
    assert out["best"] == "poisson", "no overdispersion: the extra parameter is not worth its AIC penalty."


def test_aic_values_come_from_the_discrete_models():
    df = make(500, 4, True)
    out = choose_count_model(df)
    assert out["aic_poisson"] == pytest.approx(smf.poisson("y ~ x", data=df).fit(disp=0).aic, rel=1e-9), "aic_poisson: take it from smf.poisson(...).fit().aic."


def test_lr_test_matches_scipy():
    rng = np.random.default_rng(1)
    n = 600
    d = pd.DataFrame({"x1": rng.normal(size=n), "x2": rng.normal(size=n)})
    d["y"] = rng.poisson(np.exp(0.3 + 0.5 * d["x1"] + 0.3 * d["x2"]))
    big = smf.poisson("y ~ x1 + x2", data=d).fit(disp=0)
    small = smf.poisson("y ~ x1", data=d).fit(disp=0)
    lr, df, p = lr_test(big, small)
    assert lr == pytest.approx(2 * (big.llf - small.llf)), "lr = 2 * (llf_big - llf_small)."
    assert df == 1, "the models differ by one parameter, so df = 1 (a difference, not a sum)."
    assert p == pytest.approx(stats.chi2.sf(lr, 1)), "p is the upper tail of chi-squared(df) at lr."
    assert p < 0.001, "x2 truly matters here, so the test should reject the smaller model."


def test_lr_test_on_a_useless_column_is_not_significant():
    rng = np.random.default_rng(2)
    n = 600
    d = pd.DataFrame({"x1": rng.normal(size=n), "junk": rng.normal(size=n)})
    d["y"] = rng.poisson(np.exp(0.3 + 0.5 * d["x1"]))
    big = smf.poisson("y ~ x1 + junk", data=d).fit(disp=0)
    small = smf.poisson("y ~ x1", data=d).fit(disp=0)
    lr, df, p = lr_test(big, small)
    assert lr >= -1e-9 and p > 0.001, "adding a pure-noise column should not give a tiny p-value."
