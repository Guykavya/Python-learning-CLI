import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from conftest import make_churn_regional
from solution import worst_slices


@pytest.fixture(scope="module")
def scored():
    reg = make_churn_regional()
    X = pd.get_dummies(reg.drop(columns="churned"), dtype=float)
    y = reg["churned"].to_numpy()
    Xa, Xb, ya, yb, ra, rb = train_test_split(X, y, reg, test_size=0.3, random_state=0, stratify=y)
    p = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(Xa, ya).predict_proba(Xb)[:, 1]
    return rb.reset_index(drop=True), yb, p


def test_the_planted_region_is_first(scored):
    frame, y, p = scored
    out = worst_slices(frame, y, p, ["region", "contract"])
    assert out["slice"].iloc[0] == "region=west", f"the west region was planted with unpredictable churn; it should top the list, got {out['slice'].iloc[0]}."
    assert list(out.columns) == ["slice", "rows", "gap"], "columns: slice, rows, gap."


def test_shape_order_and_sizes(scored):
    frame, y, p = scored
    out = worst_slices(frame, y, p, ["region", "contract", "autopay"], min_rows=150, top=5)
    assert len(out) == 5 and list(out.index) == list(range(5)), "the top 5, with a fresh index."
    assert out["gap"].is_monotonic_decreasing, "largest gap first."
    assert (out["rows"] >= 150).all(), "no slice smaller than min_rows."
    assert any(" & " in s for s in out["slice"]), "pairs of columns are scanned too."


def test_gap_value(scored):
    frame, y, p = scored
    out = worst_slices(frame, y, p, ["region"])
    m = (frame["region"] == "west").to_numpy()
    assert out.loc[out["slice"] == "region=west", "gap"].iloc[0] == pytest.approx(log_loss(y[m], p[m], labels=[0, 1]) - log_loss(y, p)), "gap = slice log loss minus overall log loss."
