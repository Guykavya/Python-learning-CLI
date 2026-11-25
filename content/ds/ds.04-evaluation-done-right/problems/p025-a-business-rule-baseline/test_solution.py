import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from conftest import make_churn
from solution import rule_score


def test_worked_example():
    X = pd.DataFrame({"contract_month": [1, 0, 1, 0], "support_calls": [0, 4, 3, 2]})
    out = rule_score(X)
    assert out.tolist() == [2.0, 1.0, 3.0, 0.0], "2 points for month-to-month, 1 point for 3 or more calls (>= 3)."
    assert isinstance(out, np.ndarray) and out.dtype.kind == "f", "return a float NumPy array."


def test_the_rule_is_a_real_but_beatable_baseline():
    d = make_churn(seed=0)
    X = pd.get_dummies(d.drop(columns="churned"), dtype=float)
    y = d["churned"].to_numpy()
    Xa, Xb, ya, yb = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
    rule_auc = roc_auc_score(yb, rule_score(Xb))
    model_auc = roc_auc_score(yb, make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(Xa, ya).predict_proba(Xb)[:, 1])
    assert 0.6 < rule_auc < 0.75, f"the rule alone should rank customers clearly better than chance, got {rule_auc:.3f}."
    assert model_auc > rule_auc + 0.03, "a logistic model on all features should beat the rule."
