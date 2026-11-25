import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
import statsmodels.formula.api as smf

from solution import rate_model


def make(n, seed):
    rng = np.random.default_rng(seed)
    t = rng.integers(0, 2, n)
    expo = np.where(t == 1, rng.uniform(2, 6, n), rng.uniform(1, 3, n))     # treated units are watched longer
    c = rng.poisson(expo * 0.5 * 1.5 ** t)                                # true rate ratio 1.5
    return pd.DataFrame({"count": c, "exposure": expo, "treated": t})


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_recovers_the_rate_ratio(seed):
    df = make(3000, seed)
    out = rate_model(df)
    assert out["rate_ratio"] == pytest.approx(1.5, abs=0.12), f"rate ratio {out['rate_ratio']:.2f}: the true value is 1.5. Did you pass log(exposure) as the offset?"
    assert out["ci_low"] < out["rate_ratio"] < out["ci_high"], "the interval must contain the estimate."
    assert out["ci_low"] > 1.2 and out["ci_high"] < 1.9, "with 3000 units the interval should be fairly tight around 1.5."


def test_ignoring_exposure_gives_a_very_different_answer():
    df = make(3000, 0)
    naive = smf.glm("count ~ treated", data=df, family=sm.families.Poisson()).fit()
    naive_rr = float(np.exp(naive.params["treated"]))
    assert naive_rr > 2.5, "sanity check of the test data: without an offset the ratio is inflated by the longer exposure of the treated units."
    assert rate_model(df)["rate_ratio"] < naive_rr - 1.0, "your answer looks like the naive one. Exposure must enter as an offset."


def test_matches_a_direct_fit():
    df = make(500, 7)
    res = smf.glm("count ~ treated", data=df, family=sm.families.Poisson(), offset=np.log(df["exposure"])).fit()
    out = rate_model(df)
    assert out["rate_ratio"] == pytest.approx(np.exp(res.params["treated"]), rel=1e-8), "same model, same estimate."
    lo, hi = res.conf_int().loc["treated"]
    assert (out["ci_low"], out["ci_high"]) == pytest.approx((np.exp(lo), np.exp(hi)), rel=1e-8), "interval = exp of the interval ends on the log scale."


def test_equal_exposure_gives_the_plain_count_ratio():
    df = pd.DataFrame({"count": [4, 6, 8, 12], "exposure": [1.0, 1.0, 1.0, 1.0], "treated": [0, 0, 1, 1]})
    assert rate_model(df)["rate_ratio"] == pytest.approx(10 / 5, rel=1e-6), "with equal exposure the rate ratio is the ratio of mean counts (10 / 5 = 2)."
