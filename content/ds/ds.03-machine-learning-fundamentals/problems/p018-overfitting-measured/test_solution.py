import pytest
from sklearn import datasets, linear_model, pipeline, preprocessing, tree

from solution import overfit_report

SEEDS = [0, 1, 2]


@pytest.fixture(scope="module")
def diabetes():
    return datasets.load_diabetes(return_X_y=True)


def poly2():
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(2), preprocessing.StandardScaler(), linear_model.LinearRegression())


@pytest.mark.parametrize("seed", SEEDS)
def test_linear_model_does_not_overfit(diabetes, seed):
    X, y = diabetes
    r = overfit_report(X, y, linear_model.LinearRegression(), seed)
    assert r["high_variance"] is False and r["more_data_helps"] is False, f"10 features and 350 rows: a small gap (relative {r['rel_gap']:.2f}) is not overfitting."
    assert r["gap"] < 5, "the gap of the linear model is only a few RMSE units."


@pytest.mark.parametrize("seed", SEEDS)
def test_full_tree_overfits_but_data_does_not_close_the_gap(diabetes, seed):
    X, y = diabetes
    r = overfit_report(X, y, tree.DecisionTreeRegressor(random_state=0), seed)
    assert r["high_variance"] is True and r["rel_gap"] > 0.9, "a fully grown tree has near-zero training error: the relative gap is about 1."
    assert r["more_data_helps"] is False, "the tree's gap is not shrinking as n grows: more data are not the cure here. Compare the last gap with the gap at the third point (60% of the data)."


@pytest.mark.parametrize("seed", SEEDS)
def test_polynomial_overfits_and_more_data_helps(diabetes, seed):
    X, y = diabetes
    r = overfit_report(X, y, poly2(), seed)
    assert r["high_variance"] is True, f"65 features on 350 rows overfit: relative gap {r['rel_gap']:.2f} should exceed 0.15."
    assert r["more_data_helps"] is True, "the gap of the polynomial model shrinks steadily with more rows."


def test_types(diabetes):
    X, y = diabetes
    r = overfit_report(X, y, linear_model.LinearRegression(), 0)
    assert set(r) == {"gap", "rel_gap", "high_variance", "more_data_helps"}, "return exactly these four keys."
    assert type(r["high_variance"]) is bool and type(r["more_data_helps"]) is bool and isinstance(r["gap"], float), "plain bool and float values."
