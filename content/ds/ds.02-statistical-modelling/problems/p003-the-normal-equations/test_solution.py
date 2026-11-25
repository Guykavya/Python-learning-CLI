import numpy as np
import pytest
import statsmodels.api as sm

from solution import ols_coefs


def test_worked_example():
    X = [[1, 1], [1, 2], [1, 3], [1, 4]]
    b = ols_coefs(X, [2, 3, 5, 6])
    assert np.shape(b) == (2,), "return a 1-D array with one coefficient per column of X."
    assert b == pytest.approx([0.5, 1.4]), "expected intercept 0.5 and slope 1.4: solve (X'X) b = X'y."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_statsmodels(seed):
    rng = np.random.default_rng(seed)
    n = 60
    X = np.column_stack([np.ones(n), rng.normal(size=n), rng.uniform(0, 5, size=n)])
    y = X @ [1.0, -2.0, 0.5] + rng.normal(size=n)
    ref = sm.OLS(y, X).fit().params
    got = ols_coefs(X, y)
    np.testing.assert_allclose(got, ref, rtol=1e-8, err_msg="differs from sm.OLS: X'X and X'y need @ (matrix product), not *.")


def test_perfect_fit_recovers_the_coefficients():
    rng = np.random.default_rng(9)
    X = np.column_stack([np.ones(10), rng.normal(size=10), rng.normal(size=10)])
    b_true = np.array([3.0, 1.5, -4.0])
    got = ols_coefs(X, X @ b_true)
    np.testing.assert_allclose(got, b_true, atol=1e-9, err_msg="with no noise the coefficients must come out exactly.")


def test_does_not_modify_inputs():
    X = np.array([[1.0, 1.0], [1.0, 2.0], [1.0, 4.0]])
    y = np.array([1.0, 2.0, 2.0])
    X0, y0 = X.copy(), y.copy()
    ols_coefs(X, y)
    assert np.array_equal(X, X0) and np.array_equal(y, y0), "do not change the caller's arrays."
