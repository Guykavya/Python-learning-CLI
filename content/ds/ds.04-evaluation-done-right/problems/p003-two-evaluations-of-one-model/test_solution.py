import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from conftest import make_churn
from solution import two_evaluations


def lr():
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))


def data(seed):
    d = make_churn(seed=seed, leaks=True)
    return pd.get_dummies(d.drop(columns="churned"), dtype=float), d["churned"]


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_leaky_column_is_worth_far_too_much(seed):
    X, y = data(seed)
    w, wo = two_evaluations(X, y, lr(), "retention_offer_sent")
    assert w > 0.93, f"with the post-outcome column the AUC is near 0.97, got {w:.3f}."
    assert 0.70 < wo < 0.82, f"the honest AUC without it is about 0.76, got {wo:.3f}."
    assert w - wo > 0.15, "the gap between the two evaluations is the alarm: one column must not be worth 0.2 AUC."


def test_matches_a_direct_cross_validation():
    X, y = data(0)
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    w, wo = two_evaluations(X, y, lr(), "retention_offer_sent")
    assert w == pytest.approx(cross_val_score(lr(), X, y, cv=cv, scoring="roc_auc").mean()), "use StratifiedKFold(5, shuffle=True, random_state=0) and scoring='roc_auc'."


def test_input_unchanged_and_missing_column():
    X, y = data(1)
    cols = list(X.columns)
    two_evaluations(X, y, lr(), "retention_offer_sent")
    assert list(X.columns) == cols, "do not drop the column from the caller's DataFrame."
    with pytest.raises(KeyError):
        two_evaluations(X, y, lr(), "no_such_column")
