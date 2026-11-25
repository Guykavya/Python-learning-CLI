import pandas as pd
import pytest
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier

from conftest import make_churn
from solution import single_feature_auc


@pytest.fixture(scope="module", params=[0, 1, 2])
def result(request):
    d = make_churn(seed=request.param, leaks=True)
    X = pd.get_dummies(d.drop(columns="churned"), dtype=float)
    return X, d["churned"], single_feature_auc(X, d["churned"])


def test_the_planted_leak_comes_first(result):
    X, y, s = result
    assert s.index[0] == "retention_offer_sent", f"the post-outcome column must top the list, got {s.index[0]}."
    assert s.iloc[0] > 0.9 and s.iloc[1] < 0.75, "the leak scores above 0.9 alone; honest features stay in the 0.5-0.7 range."


def test_sorted_series_with_every_column(result):
    X, y, s = result
    assert isinstance(s, pd.Series) and s.name == "single_feature_auc", "return a Series named 'single_feature_auc'."
    assert set(s.index) == set(X.columns), "one score per column."
    assert list(s.values) == sorted(s.values, reverse=True), "sort from the highest score to the lowest."


def test_values_match_a_direct_computation(result):
    X, y, s = result
    direct = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), X[["support_calls"]], y, cv=5, scoring="roc_auc").mean()
    assert s["support_calls"] == pytest.approx(direct), "use DecisionTreeClassifier(max_depth=3, random_state=0) on the single column, cv folds, scoring='roc_auc'."
