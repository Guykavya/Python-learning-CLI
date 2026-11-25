import numpy as np
import pandas as pd
import pytest

from solution import lasso_selected


def make(seed, n=300):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 10))
    y = 3 * X[:, 0] + 2 * X[:, 1] - 2 * X[:, 2] + rng.normal(size=n)
    return pd.DataFrame(X, columns=[f"x{i}" for i in range(10)]), y


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
def test_keeps_exactly_the_three_real_features(seed):
    X, y = make(seed)
    assert lasso_selected(X, y, 0.3) == ["x0", "x1", "x2"], "at alpha = 0.3 only the three real features have non-zero coefficients (names in column order)."


def test_huge_alpha_removes_everything():
    X, y = make(0)
    assert lasso_selected(X, y, 10.0) == [], "with a very large penalty every coefficient is exactly zero."


def test_tiny_alpha_keeps_almost_everything():
    X, y = make(0)
    assert len(lasso_selected(X, y, 0.001)) >= 8, "with almost no penalty the junk features keep small non-zero coefficients."


def test_scaling_makes_units_irrelevant():
    X, y = make(1)
    X2 = X.copy()
    X2["x0"] = X2["x0"] * 1000.0              # change the unit of one real feature
    assert lasso_selected(X2, y, 0.3) == lasso_selected(X, y, 0.3), "after standardising, the unit of a column must not change the selection."


def test_negative_alpha():
    X, y = make(0)
    with pytest.raises(ValueError):
        lasso_selected(X, y, -0.1)
