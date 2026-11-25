import warnings

import numpy as np
import pytest
import statsmodels.api as sm

from solution import safe_logit


def separable():
    x = np.array([-3, -2, -1, -0.5, 0.5, 1, 2, 3.0])
    y = (x > 0).astype(int)
    return sm.add_constant(x), y


def normal(seed=0, n=300):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=n)
    y = (rng.random(n) < 1 / (1 + np.exp(-(0.2 + 1.0 * x)))).astype(int)
    return sm.add_constant(x), y


def test_separated_data_is_refused():
    X, y = separable()
    with warnings.catch_warnings():
        warnings.simplefilter("error")           # a leaking warning would turn into an error here
        res, reason = safe_logit(X, y)
    assert res is None, "perfectly separated data has no finite estimate: return None, do not return the huge-coefficient fit."
    assert "separation" in reason.lower(), f"the reason must mention separation, got {reason!r}."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_normal_data_is_fitted(seed):
    X, y = normal(seed)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        res, reason = safe_logit(X, y)
    assert res is not None and reason == "ok", f"an ordinary data set must fit and give reason 'ok'; got {reason!r}."
    assert res.params[1] == pytest.approx(1.0, abs=0.45), "the fitted slope should be near the true 1.0."


def test_a_binary_predictor_that_predicts_perfectly():
    rng = np.random.default_rng(3)
    g = rng.integers(0, 2, 200)
    y = g.copy()                                 # group 1 is always positive, group 0 never
    res, reason = safe_logit(sm.add_constant(g.astype(float)), y)
    assert res is None and "separation" in reason.lower(), "a 0/1 predictor equal to the outcome is separation as well."


def test_singular_design():
    rng = np.random.default_rng(4)
    x = rng.normal(size=100)
    y = (rng.random(100) < 0.5).astype(int)
    X = np.column_stack([np.ones(100), x, 2 * x])         # third column = 2 * second
    res, reason = safe_logit(X, y)
    assert res is None and "singular" in reason.lower(), f"a column that is a copy of another gives a singular matrix; reason {reason!r}."


def test_unrelated_errors_are_not_swallowed():
    with pytest.raises(Exception):
        safe_logit(sm.add_constant(np.arange(5.0)), np.array([0, 1, 2, 3, 4]))     # y is not 0/1: a real error, not separation
