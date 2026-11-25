import numpy as np
import pytest
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from solution import ridge_pipeline


def data(seed=0, n=200):
    rng = np.random.default_rng(seed)
    z1, z2 = rng.normal(size=n), rng.normal(size=n)
    X = np.column_stack([1000 * z1, z2])               # same effect per standard deviation, very different units
    y = 3 * z1 + 3 * z2 + 0.5 * rng.normal(size=n)
    return X, y


def test_structure():
    p = ridge_pipeline(5.0)
    assert isinstance(p, Pipeline) and len(p.steps) == 2, "a Pipeline with two steps."
    assert isinstance(p.steps[0][1], StandardScaler), "the scaler must come first."
    assert isinstance(p.steps[1][1], Ridge) and p.steps[1][1].alpha == 5.0, "then Ridge with the given alpha."


def test_it_is_not_fitted_yet():
    assert not hasattr(ridge_pipeline(1.0).steps[0][1], "mean_"), "return an unfitted pipeline."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_both_features_are_penalised_equally(seed):
    X, y = data(seed)
    p = ridge_pipeline(2000.0).fit(X, y)
    b = p[-1].coef_
    ratio = b[0] / b[1]
    assert 0.75 < ratio < 1.35, f"after scaling the two equally useful features must get similar coefficients, ratio {ratio:.2f}."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_unscaled_ridge_treats_them_very_unequally(seed):
    X, y = data(seed)
    raw = Ridge(alpha=2000.0).fit(X, y)
    standardised = raw.coef_ * X.std(axis=0)
    assert standardised[0] / standardised[1] > 4, "sanity check of the test data: without scaling the big-unit feature is hardly shrunk."


def test_predictions_work_on_new_rows():
    X, y = data(0)
    p = ridge_pipeline(1.0).fit(X[:150], y[:150])
    assert p.predict(X[150:]).shape == (50,), "the pipeline must predict on unseen rows."
