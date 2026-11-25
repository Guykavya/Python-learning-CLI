import numpy as np
import pytest
from sklearn.metrics import f1_score

from solution import multiclass_f1

Y = np.array([0, 0, 0, 0, 0, 0, 1, 1, 2])
P = np.array([0, 0, 0, 0, 0, 0, 1, 0, 0])


def test_the_three_averages_differ_on_an_imbalanced_case():
    out = multiclass_f1(Y, P)
    assert out["macro"] == pytest.approx(f1_score(Y, P, average="macro"), rel=1e-10), "macro = plain mean of the per-class F1."
    assert out["micro"] == pytest.approx(f1_score(Y, P, average="micro"), rel=1e-10), "micro = F1 from the pooled TP, FP, FN (equals accuracy here)."
    assert out["weighted"] == pytest.approx(f1_score(Y, P, average="weighted"), rel=1e-10), "weighted = mean weighted by the true rows of each class."
    assert abs(out["macro"] - out["micro"]) > 0.02, "on this imbalanced example macro and micro must differ."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_sklearn_on_random_labels(seed):
    rng = np.random.default_rng(seed)
    y = rng.choice([0, 1, 2, 3], size=300, p=[0.6, 0.25, 0.1, 0.05])
    p = np.where(rng.random(300) < 0.7, y, rng.integers(0, 4, 300))
    out = multiclass_f1(y, p)
    for avg in ("macro", "micro", "weighted"):
        assert out[avg] == pytest.approx(f1_score(y, p, average=avg, zero_division=0), rel=1e-10), f"{avg} average differs from sklearn."


def test_a_class_that_is_never_predicted_scores_zero():
    y = np.array([0, 0, 0, 1, 1, 2])
    p = np.array([0, 0, 0, 1, 1, 0])
    out = multiclass_f1(y, p)
    assert out["macro"] == pytest.approx(f1_score(y, p, average="macro", zero_division=0)), "class 2 is never predicted: its F1 is 0.0 and still counts in the macro mean."


def test_a_class_only_in_the_predictions_counts_too():
    y = np.array([0, 0, 1, 1])
    p = np.array([0, 2, 1, 1])
    assert multiclass_f1(y, p)["macro"] == pytest.approx(f1_score(y, p, average="macro", zero_division=0)), "class 2 appears only in p: it has support 0 and F1 0.0."


def test_micro_equals_accuracy_for_single_label_problems():
    rng = np.random.default_rng(5)
    y = rng.integers(0, 3, 200)
    p = rng.integers(0, 3, 200)
    assert multiclass_f1(y, p)["micro"] == pytest.approx(np.mean(y == p)), "pooling all classes, micro F1 equals the accuracy."


def test_length_mismatch():
    with pytest.raises(ValueError):
        multiclass_f1([0, 1], [0])
