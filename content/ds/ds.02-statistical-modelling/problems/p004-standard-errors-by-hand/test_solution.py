import numpy as np
import pytest
import statsmodels.api as sm

from solution import ols_se


def test_worked_example():
    se = ols_se([[1, 1], [1, 2], [1, 3], [1, 4]], [2, 3, 5, 6])
    assert se == pytest.approx([0.38730, 0.14142], rel=1e-3), "hand check: RSS = 0.2, sigma2 = 0.2 / (4 - 2) = 0.1, inv(X'X) = [[1.5, -0.5], [-0.5, 0.2]], se = sqrt([0.15, 0.02])."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_statsmodels(seed):
    rng = np.random.default_rng(seed)
    n = 30
    X = np.column_stack([np.ones(n), rng.normal(size=n), rng.normal(size=n)])
    y = X @ [2.0, 1.0, -1.0] + rng.normal(0, 1.5, size=n)
    ref = sm.OLS(y, X).fit().bse
    np.testing.assert_allclose(ols_se(X, y), ref, rtol=1e-8,
                               err_msg="differs from statsmodels bse. Divide RSS by n - p (degrees of freedom), not by n.")


def test_small_sample_exposes_the_divisor():
    X = np.column_stack([np.ones(5), [0.0, 1.0, 2.0, 3.0, 4.0]])
    y = np.array([1.0, 0.0, 2.0, 1.0, 3.0])
    ref = sm.OLS(y, X).fit().bse
    np.testing.assert_allclose(ols_se(X, y), ref, rtol=1e-9, err_msg="with only 5 rows, using n instead of n - p is clearly wrong.")


def test_more_data_shrinks_the_standard_error():
    rng = np.random.default_rng(7)
    def slope_se(n):
        x = rng.normal(size=n)
        X = np.column_stack([np.ones(n), x])
        y = 1 + 2 * x + rng.normal(size=n)
        return ols_se(X, y)[1]
    assert slope_se(2000) < slope_se(40), "standard errors fall roughly like 1/sqrt(n)."
