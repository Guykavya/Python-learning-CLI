import numpy as np
import pytest
from sklearn import datasets
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from solution import tune

GRID = {"ridge__alpha": np.logspace(-3, 3, 13)}


def model():
    return make_pipeline(StandardScaler(), Ridge())


def test_matches_a_direct_search():
    X, y = datasets.load_diabetes(return_X_y=True)
    params, score = tune(model(), GRID, X, y, "neg_root_mean_squared_error")
    gs = GridSearchCV(model(), GRID, cv=5, scoring="neg_root_mean_squared_error").fit(X, y)
    assert params == gs.best_params_, "the best parameters of a 5-fold GridSearchCV."
    assert score == pytest.approx(gs.best_score_), "the mean cross-validated score of the best setting (negative for neg_ scorers)."


def test_sensible_values_on_diabetes():
    X, y = datasets.load_diabetes(return_X_y=True)
    params, score = tune(model(), GRID, X, y, "neg_root_mean_squared_error")
    assert 0.01 <= params["ridge__alpha"] <= 30, f"best alpha {params['ridge__alpha']}: on this data a small penalty is best."
    assert -57 < score < -52, "the cross-validated RMSE on the diabetes data is about 54.7."


def test_default_scoring_is_r2():
    X, y = datasets.load_diabetes(return_X_y=True)
    _, score = tune(model(), GRID, X, y)
    assert 0.4 < score < 0.55, "with scoring=None a Ridge pipeline is scored with R-squared (about 0.48)."


def test_returns_python_types():
    X, y = datasets.load_diabetes(return_X_y=True)
    params, score = tune(model(), {"ridge__alpha": [0.1, 10.0]}, X, y)
    assert isinstance(params, dict) and isinstance(score, float), "return (dict, float)."
