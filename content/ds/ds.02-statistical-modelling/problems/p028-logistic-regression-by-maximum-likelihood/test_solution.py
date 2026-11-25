import numpy as np
import pytest
import statsmodels.api as sm

from solution import fit_logit


def make(seed, n=500):
    rng = np.random.default_rng(seed)
    X = np.column_stack([np.ones(n), rng.normal(size=n), rng.normal(size=n)])
    p = 1 / (1 + np.exp(-(X @ [-0.5, 1.0, -0.8])))
    y = (rng.random(n) < p).astype(float)
    return X, y


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_statsmodels(seed):
    X, y = make(seed)
    ref = sm.Logit(y, X).fit(disp=0).params
    np.testing.assert_allclose(fit_logit(X, y), ref, atol=1e-4, err_msg="differs from sm.Logit. Newton step: b += solve(X' W X, X'(y - p)) with W = p(1 - p).")


def test_gradient_is_zero_at_the_solution():
    X, y = make(3)
    b = fit_logit(X, y)
    p = 1 / (1 + np.exp(-(X @ b)))
    assert np.max(np.abs(X.T @ (y - p))) < 1e-6, "at the maximum of the likelihood the gradient X'(y - p) must be (nearly) zero: iterate until the step is tiny."


def test_likelihood_beats_the_zero_start():
    X, y = make(4)
    def ll(b):
        z = X @ b
        return np.sum(y * z - np.log1p(np.exp(z)))
    assert ll(fit_logit(X, y)) > ll(np.zeros(3)) + 10, "the fitted coefficients must have a clearly higher log-likelihood than b = 0."


def test_returns_a_1d_array_and_leaves_inputs_alone():
    X, y = make(5)
    X0, y0 = X.copy(), y.copy()
    b = fit_logit(X, y)
    assert b.shape == (3,), "return a 1-D array, one coefficient per column."
    assert np.array_equal(X, X0) and np.array_equal(y, y0), "do not modify the inputs."
