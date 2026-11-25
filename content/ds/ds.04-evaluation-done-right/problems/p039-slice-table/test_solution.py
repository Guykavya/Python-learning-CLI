import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from conftest import make_churn_regional
from solution import slice_table


@pytest.fixture(scope="module")
def scored():
    reg = make_churn_regional(n=8000)
    X = pd.get_dummies(reg.drop(columns="churned"), dtype=float)
    y = reg["churned"].to_numpy()
    Xa, Xb, ya, yb, ra, rb = train_test_split(X, y, reg, test_size=0.3, random_state=0, stratify=y)
    p = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(Xa, ya).predict_proba(Xb)[:, 1]
    return rb.reset_index(drop=True), yb, p


def test_the_weak_region_shows_up(scored):
    frame, y, p = scored
    t = slice_table(frame, y, p, "region")
    assert list(t.index) == ["east", "north", "south", "west"], "one row per region, sorted."
    assert list(t.columns) == ["rows", "base_rate", "mean_p", "auc"], "columns: rows, base_rate, mean_p, auc."
    assert t["auc"].idxmin() == "west" and t.loc["west", "auc"] < 0.6, "the planted region (west) has an AUC near 0.5."
    assert t["rows"].sum() == len(y), "every row in exactly one slice."


def test_values_for_one_slice(scored):
    frame, y, p = scored
    t = slice_table(frame, y, p, "contract")
    m = (frame["contract"] == "year").to_numpy()
    assert t.loc["year", "rows"] == m.sum() and t.loc["year", "base_rate"] == pytest.approx(y[m].mean()), "rows and base rate of the slice."
    assert t.loc["year", "auc"] == pytest.approx(roc_auc_score(y[m], p[m])), "AUC inside the slice."


def test_one_class_slice_gives_nan():
    frame = pd.DataFrame({"g": ["a", "a", "b", "b", "b"]}, index=[10, 11, 12, 13, 14])
    t = slice_table(frame, np.array([1, 1, 0, 1, 0]), np.array([0.9, 0.8, 0.2, 0.7, 0.4]), "g")
    assert np.isnan(t.loc["a", "auc"]), "slice 'a' has only positives: AUC is NaN, not a crash."
    assert t.loc["b", "auc"] == pytest.approx(1.0), "slice 'b' is ranked perfectly. Use positions, not the frame's index labels."
