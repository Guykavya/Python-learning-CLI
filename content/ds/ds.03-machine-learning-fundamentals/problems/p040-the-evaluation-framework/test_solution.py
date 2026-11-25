import numpy as np
import pytest
from sklearn import datasets, dummy, linear_model, model_selection, pipeline, preprocessing, tree

from solution import Evaluation, TestSetAlreadyOpened


def ridge(alpha=1.0):
    return pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.Ridge(alpha=alpha))


@pytest.fixture(scope="module")
def diabetes():
    return datasets.load_diabetes(return_X_y=True)


@pytest.fixture(scope="module")
def cancer():
    return datasets.load_breast_cancer(return_X_y=True)


def test_split_is_made_once_and_stratified(diabetes, cancer):
    X, y = diabetes
    ev = Evaluation(X, y, "regression", test_size=0.2, seed=0)
    X_dev, X_te, y_dev, y_te = model_selection.train_test_split(X, y, test_size=0.2, random_state=0)
    assert np.array_equal(ev.X_dev, X_dev) and np.array_equal(ev._y_test, y_te), "split with train_test_split(test_size, random_state=seed)."
    Xc, yc = cancer
    evc = Evaluation(Xc, yc, "classification", seed=0)
    assert abs(evc._y_test.mean() - yc.mean()) < 0.02, "classification splits must be stratified."
    assert len(evc.y_dev) + len(evc._y_test) == len(yc), "every row is either development or test."


def test_bad_task(diabetes):
    with pytest.raises(ValueError):
        Evaluation(*diabetes, task="ranking")


def test_baseline_regression_and_classification(diabetes, cancer):
    X, y = diabetes
    ev = Evaluation(X, y, "regression", seed=0)
    base = ev.baseline()
    direct = -model_selection.cross_val_score(dummy.DummyRegressor(), ev.X_dev, ev.y_dev, cv=ev.cv, scoring="neg_root_mean_squared_error")
    assert base["cv_mean"] == pytest.approx(direct.mean()), "baseline = cross-validated RMSE of DummyRegressor on the development data."
    assert base["model"] == "baseline", "the row is called 'baseline'."
    Xc, yc = cancer
    evc = Evaluation(Xc, yc, "classification", seed=0)
    b = evc.baseline()
    assert b["cv_mean"] == pytest.approx(0.626, abs=0.02), "the majority-class accuracy of the breast cancer data is about 0.63."


def test_compare_sorts_best_first(diabetes, cancer):
    X, y = diabetes
    ev = Evaluation(X, y, "regression", seed=0)
    table = ev.compare({"ridge": ridge(), "tree": tree.DecisionTreeRegressor(random_state=0), "mean": dummy.DummyRegressor()})
    assert list(table.columns) == ["model", "cv_mean", "cv_sd"], "columns: model, cv_mean, cv_sd."
    assert table["cv_mean"].is_monotonic_increasing, "regression: RMSE, smallest first."
    assert table["model"].iloc[0] == "ridge", "ridge is the best of the three on the diabetes data."
    assert table["cv_mean"].iloc[0] == pytest.approx(53.8, abs=1.5), "cross-validated RMSE of ridge: about 53.8 (a positive number)."
    Xc, yc = cancer
    evc = Evaluation(Xc, yc, "classification", seed=0)
    t = evc.compare({"logistic": pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.LogisticRegression(max_iter=2000)),
                     "majority": dummy.DummyClassifier(strategy="most_frequent")})
    assert t["cv_mean"].is_monotonic_decreasing and t["model"].iloc[0] == "logistic", "classification: accuracy, largest first."


def test_learning_curve_and_diagnose(diabetes):
    X, y = diabetes
    ev = Evaluation(X, y, "regression", seed=0)
    lc = ev.learning_curve(tree.DecisionTreeRegressor(random_state=0))
    assert list(lc.columns) == ["n_train", "train", "validation", "gap"], "columns: n_train, train, validation, gap."
    assert len(lc) == 5 and (lc["validation"] > 0).all(), "five sizes; errors are positive."
    assert lc["train"].iloc[-1] < 1e-6, "a fully grown tree has zero training error."
    assert Evaluation.diagnose(lc).startswith("high variance"), "a zero training error and a large validation error: high variance."
    lc2 = ev.learning_curve(ridge())
    assert Evaluation.diagnose(lc2).startswith("high bias or near the noise floor"), "the ridge model has a small gap."


def test_diagnose_classification_uses_the_error():
    import pandas as pd
    lc = pd.DataFrame({"n_train": [100, 300], "train": [1.0, 1.0], "validation": [0.90, 0.94]})
    lc["gap"] = lc["train"] - lc["validation"]
    assert Evaluation.diagnose(lc, "classification").startswith("high variance"), "error 0.06, gap 0.06: relative gap 1.0."


def test_tune_returns_a_refit_best_model(diabetes):
    X, y = diabetes
    ev = Evaluation(X, y, "regression", seed=0)
    best, params, score = ev.tune(ridge(), {"ridge__alpha": [0.01, 1.0, 10.0, 1000.0]})
    assert params["ridge__alpha"] in (0.01, 1.0, 10.0), "a huge penalty cannot win on this data."
    assert 52 < score < 56, "cv RMSE of the best ridge is about 53.7 (positive)."
    assert hasattr(best, "predict"), "return the refitted best estimator."


def test_the_test_set_opens_exactly_once(diabetes):
    X, y = diabetes
    ev = Evaluation(X, y, "regression", seed=0)
    best, _, _ = ev.tune(ridge(), {"ridge__alpha": [1.0, 10.0]})
    first = ev.final_test(best)
    assert set(first) == {"RMSE", "MAE", "R2"} and 50 < first["RMSE"] < 66, f"final regression metrics, RMSE about 58, got {first}."
    with pytest.raises(TestSetAlreadyOpened):
        ev.final_test(best)
    assert issubclass(TestSetAlreadyOpened, RuntimeError), "TestSetAlreadyOpened is a RuntimeError."


def test_final_test_fits_on_development_data_only(diabetes):
    X, y = diabetes
    ev = Evaluation(X, y, "regression", seed=0)
    seen = []

    class Spy(linear_model.LinearRegression):
        def fit(self, X_, y_, *a, **k):
            seen.append(len(y_))
            return super().fit(X_, y_, *a, **k)

    ev.final_test(Spy())
    assert seen == [len(ev.y_dev)], f"fit on the development rows only ({len(ev.y_dev)}), saw {seen}."


def test_classification_final_test(cancer):
    Xc, yc = cancer
    ev = Evaluation(Xc, yc, "classification", seed=0)
    res = ev.final_test(pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.LogisticRegression(max_iter=2000)))
    assert set(res) == {"accuracy", "precision", "recall", "F1"}, "classification metrics: accuracy, precision, recall, F1."
    assert res["accuracy"] > 0.95 and all(type(v) is float for v in res.values()), "the logistic model reaches about 0.98 on this split."


def test_honesty_on_fake_data():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(400, 5))
    noisy = Evaluation(X, rng.normal(size=400), "regression", seed=1)
    assert noisy.final_test(linear_model.LinearRegression())["R2"] < 0.1, "a target that is pure noise must not be 'predictable': R2 near 0 on the sealed test set."
    exact = Evaluation(X, X @ np.array([1.0, 2.0, 0.0, 0.0, -1.0]), "regression", seed=1)
    assert exact.final_test(linear_model.LinearRegression())["R2"] > 0.999, "a deterministic target must give R2 near 1."
