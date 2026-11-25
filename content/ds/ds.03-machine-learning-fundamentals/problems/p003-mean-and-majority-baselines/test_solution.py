import numpy as np
import pytest
from sklearn.dummy import DummyClassifier, DummyRegressor

from solution import baseline_predict


def test_regression_examples():
    out = baseline_predict([1, 2, 3, 6], 3, "regression")
    assert out.tolist() == [3.0, 3.0, 3.0], "the baseline for regression is the mean of the training targets, repeated n times."


def test_classification_examples():
    assert baseline_predict([0, 1, 1, 2], 2, "classification").tolist() == [1, 1], "predict the most frequent training class."
    assert baseline_predict([0, 0, 1, 1], 2, "classification").tolist() == [0, 0], "on a tie take the smaller class."
    assert baseline_predict([2, 2, 1, 1], 1, "classification").tolist() == [1], "on a tie take the smaller class, whatever the order of the data."


def test_matches_dummy_estimators():
    rng = np.random.default_rng(0)
    y = rng.normal(5, 2, 50)
    X = np.zeros((50, 1))
    ref = DummyRegressor().fit(X, y).predict(np.zeros((7, 1)))
    assert baseline_predict(y, 7, "regression") == pytest.approx(ref), "same as DummyRegressor."
    c = rng.choice([0, 1, 2], size=60, p=[0.2, 0.5, 0.3])
    refc = DummyClassifier(strategy="most_frequent").fit(np.zeros((60, 1)), c).predict(np.zeros((4, 1)))
    assert baseline_predict(c, 4, "classification").tolist() == refc.tolist(), "same as DummyClassifier(strategy='most_frequent')."


def test_length_and_type():
    out = baseline_predict([1, 2, 3], 5, "regression")
    assert isinstance(out, np.ndarray) and out.shape == (5,), "return a NumPy array of length n."


def test_unknown_task():
    with pytest.raises(ValueError):
        baseline_predict([1, 2], 2, "clustering")
