import numpy as np
import pytest
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan

from solution import hetero_check


def fit(n, seed, hetero):
    rng = np.random.default_rng(seed)
    x = rng.exponential(3, n)
    e = rng.normal(0, 1, n) * ((0.2 + x) if hetero else 1.5)
    return sm.OLS(1 + 2 * x + e, sm.add_constant(x)).fit()


def test_keys():
    out = hetero_check(fit(200, 0, True))
    assert set(out) == {"bp_p", "se_ordinary", "se_robust"}, f"expected keys bp_p, se_ordinary, se_robust; got {sorted(out)}."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_test_detects_heteroscedasticity(seed):
    out = hetero_check(fit(400, seed, True))
    assert out["bp_p"] < 0.01, f"p = {out['bp_p']:.3g}: the spread grows strongly with x, Breusch-Pagan should reject. Use the residuals and the model's exog."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_no_alarm_on_clean_data(seed):
    out = hetero_check(fit(400, seed, False))
    assert out["bp_p"] > 0.001, f"p = {out['bp_p']:.3g}: constant-variance errors should not give a tiny p."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_robust_slope_se_is_larger_when_variance_grows(seed):
    out = hetero_check(fit(400, seed, True))
    assert out["se_robust"][1] > 1.3 * out["se_ordinary"][1], "ordinary SEs understate the slope uncertainty here; HC3 should be clearly larger."


def test_ordinary_se_is_result_bse_and_values_are_arrays():
    res = fit(200, 3, True)
    out = hetero_check(res)
    assert np.allclose(out["se_ordinary"], res.bse), "se_ordinary is result.bse."
    assert isinstance(out["se_robust"], np.ndarray) and out["se_robust"].shape == (2,), "se_robust is a NumPy array with one value per coefficient."
    expected = res.get_robustcov_results("HC3").bse
    assert np.allclose(out["se_robust"], expected), "se_robust must be HC3."
    lm, lm_p, f, f_p = het_breuschpagan(res.resid, res.model.exog)
    assert out["bp_p"] == pytest.approx(lm_p), "bp_p is the second value (LM p-value) of het_breuschpagan."
