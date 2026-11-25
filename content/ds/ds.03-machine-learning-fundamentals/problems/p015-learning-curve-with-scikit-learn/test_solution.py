import numpy as np
import pytest
from sklearn import datasets, linear_model, model_selection, pipeline, preprocessing, tree

from solution import real_curve


def direct(est, X, y, scoring):
    return model_selection.learning_curve(est, X, y, train_sizes=[0.1, 0.2, 0.4, 0.7, 1.0],
                                          cv=model_selection.KFold(5, shuffle=True, random_state=0), scoring=scoring)


def test_regression_errors_are_positive_and_match_sklearn():
    X, y = datasets.load_diabetes(return_X_y=True)
    out = real_curve(linear_model.LinearRegression(), X, y)
    sizes, tr, va = direct(linear_model.LinearRegression(), X, y, "neg_root_mean_squared_error")
    assert list(out.columns) == ["n_train", "train", "validation", "gap"], "columns: n_train, train, validation, gap."
    assert out["n_train"].tolist() == sizes.tolist(), "n_train is the array of sizes learning_curve returns."
    assert out["train"].to_numpy() == pytest.approx(-tr.mean(axis=1)), "train = mean over folds (axis=1), sign flipped for neg_ scorers."
    assert out["validation"].to_numpy() == pytest.approx(-va.mean(axis=1)), "validation = mean over folds, sign flipped."
    assert (out["train"] > 0).all() and (out["validation"] > 0).all(), "errors must be positive numbers."
    assert out["gap"].to_numpy() == pytest.approx(out["validation"].to_numpy() - out["train"].to_numpy()), "for an error the gap is validation - train."


def test_the_gap_of_a_flexible_model_is_larger():
    X, y = datasets.load_diabetes(return_X_y=True)
    lin = real_curve(linear_model.LinearRegression(), X, y)
    deep = real_curve(tree.DecisionTreeRegressor(random_state=0), X, y)
    assert deep["gap"].iloc[-1] > 10 * lin["gap"].iloc[-1], "a fully grown tree memorises: its final gap must dwarf the linear model's."


def test_accuracy_scorer_is_not_flipped():
    X, y = datasets.load_breast_cancer(return_X_y=True)
    est = pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.LogisticRegression(max_iter=2000))
    out = real_curve(est, X, y, scoring="accuracy")
    sizes, tr, va = direct(est, X, y, "accuracy")
    assert out["train"].to_numpy() == pytest.approx(tr.mean(axis=1)), "accuracy is a score: do NOT flip the sign."
    assert out["gap"].to_numpy() == pytest.approx(out["train"].to_numpy() - out["validation"].to_numpy()), "for a score the gap is train - validation."
    assert (out["train"] <= 1).all() and (out["train"] > 0.8).all(), "accuracies are between 0 and 1."
