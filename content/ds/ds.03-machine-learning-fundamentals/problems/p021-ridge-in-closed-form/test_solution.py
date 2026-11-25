import numpy as np
import pytest
from sklearn.linear_model import LinearRegression, Ridge

from solution import ridge_fit


def make(seed, n=80, k=4):
    rng = np.random.default_rng(seed)
    X = rng.normal(5, 3, size=(n, k))              # not centred on purpose
    y = 10 + X @ np.array([2.0, -1.0, 0.5, 0.0]) + rng.normal(size=n)
    return X, y


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("alpha", [0.5, 10.0, 300.0])
def test_matches_sklearn_ridge(seed, alpha):
    X, y = make(seed)
    b0, b = ridge_fit(X, y, alpha)
    ref = Ridge(alpha=alpha).fit(X, y)
    np.testing.assert_allclose(b, ref.coef_, rtol=1e-8, atol=1e-10, err_msg="coefficients differ from sklearn Ridge: centre X and y, then solve (Xc'Xc + alpha I) b = Xc'yc.")
    assert b0 == pytest.approx(ref.intercept_, rel=1e-8), "intercept = mean(y) - mean(X) @ beta, and it is not penalised."


def test_alpha_zero_is_ordinary_least_squares():
    X, y = make(3)
    b0, b = ridge_fit(X, y, 0.0)
    ols = LinearRegression().fit(X, y)
    np.testing.assert_allclose(b, ols.coef_, rtol=1e-8, atol=1e-10, err_msg="alpha = 0 must give the least-squares coefficients.")


def test_larger_alpha_shrinks_the_coefficients():
    X, y = make(4)
    norms = [np.linalg.norm(ridge_fit(X, y, a)[1]) for a in (0, 1, 100, 10000)]
    assert norms == sorted(norms, reverse=True), "the coefficient vector must get shorter as alpha grows."
    assert ridge_fit(X, y, 1e9)[0] == pytest.approx(y.mean(), rel=1e-3), "with a huge alpha the model predicts the mean: intercept -> mean(y)."


def test_intercept_is_not_penalised():
    X, y = make(5)
    y_shifted = y + 1000.0
    b0, b = ridge_fit(X, y, 50.0)
    c0, c = ridge_fit(X, y_shifted, 50.0)
    assert c0 - b0 == pytest.approx(1000.0, rel=1e-9), "adding a constant to y must move only the intercept, by exactly that constant."
    np.testing.assert_allclose(c, b, rtol=1e-9, err_msg="and must not change the slopes.")


def test_negative_alpha():
    X, y = make(0)
    with pytest.raises(ValueError):
        ridge_fit(X, y, -1.0)
