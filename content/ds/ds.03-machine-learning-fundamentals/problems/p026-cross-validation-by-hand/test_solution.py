import numpy as np
import pytest
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score

from solution import cross_val_manual


def make(seed, n=60):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 3))
    y = X @ [1.0, -2.0, 0.5] + rng.normal(size=n)
    return X, y


def folds_for(n, k, seed):
    return np.array_split(np.random.default_rng(seed).permutation(n), k)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_equals_cross_val_score_with_the_same_folds(seed):
    X, y = make(seed)
    folds = folds_for(60, 5, seed)
    pairs = [(np.setdiff1d(np.arange(60), f), f) for f in folds]
    expected = cross_val_score(Ridge(alpha=1.0), X, y, cv=pairs, scoring="r2")
    got = cross_val_manual(lambda: Ridge(alpha=1.0), X, y, folds, r2_score)
    np.testing.assert_allclose(got, expected, rtol=1e-9, err_msg="scores differ from cross_val_score with the same folds: train on the rows NOT in the fold, score only the fold.")


def test_one_score_per_fold_in_order():
    X, y = make(3)
    folds = folds_for(60, 4, 0)
    out = cross_val_manual(LinearRegression, X, y, folds, r2_score)
    assert out.shape == (4,), "one score per fold, as a NumPy array."
    m = LinearRegression().fit(X[np.setdiff1d(np.arange(60), folds[2])], y[np.setdiff1d(np.arange(60), folds[2])])
    assert out[2] == pytest.approx(r2_score(y[folds[2]], m.predict(X[folds[2]]))), "entry i belongs to folds[i]."


def test_a_fresh_model_per_fold():
    X, y = make(4)
    built = []

    def make_model():
        m = LinearRegression()
        built.append(m)
        return m

    cross_val_manual(make_model, X, y, folds_for(60, 5, 0), r2_score)
    assert len(built) == 5 and len(set(map(id, built))) == 5, "call make_model() once per fold."


def test_the_validation_fold_is_never_used_for_fitting():
    X, y = make(5)
    folds = folds_for(60, 5, 1)
    seen = []

    class Spy(LinearRegression):
        def fit(self, X_, y_, *a, **k):
            seen.append(len(y_))
            return super().fit(X_, y_, *a, **k)

    cross_val_manual(Spy, X, y, folds, r2_score)
    assert seen == [60 - len(f) for f in folds], f"each fit must see only the rows outside its fold, got sizes {seen}."
