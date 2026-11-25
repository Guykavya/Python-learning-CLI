import warnings

import numpy as np
import pytest
from sklearn import metrics

from solution import cls_metrics


def test_worked_example():
    out = cls_metrics(8, 2, 4, 86)
    assert out["accuracy"] == pytest.approx(0.94), "accuracy = (8 + 86) / 100."
    assert out["precision"] == pytest.approx(0.8), "precision = TP / (TP + FP) = 8 / 10."
    assert out["recall"] == pytest.approx(8 / 12), "recall = TP / (TP + FN) = 8 / 12."
    assert out["specificity"] == pytest.approx(86 / 88), "specificity = TN / (TN + FP)."
    assert out["f1"] == pytest.approx(2 * 0.8 * (8 / 12) / (0.8 + 8 / 12)), "F1 is the harmonic mean of precision and recall."


def test_the_always_no_model_has_no_warning():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        out = cls_metrics(0, 0, 20, 980)
    assert out["accuracy"] == pytest.approx(0.98), "98% accuracy..."
    assert out["precision"] == 0.0 and out["recall"] == 0.0 and out["f1"] == 0.0, "...but a zero denominator must give 0.0 (no exception, no warning, no nan)."


def test_other_zero_denominators():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert cls_metrics(0, 5, 0, 0)["recall"] == 0.0, "no real positives: recall is 0.0 by convention."
        assert cls_metrics(0, 0, 0, 0)["accuracy"] == 0.0, "no rows at all: 0.0."
        assert cls_metrics(5, 0, 0, 0)["specificity"] == 0.0, "no real negatives: specificity is 0.0."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_sklearn(seed):
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, 200)
    p = np.where(rng.random(200) < 0.8, y, 1 - y)
    TP = int(((y == 1) & (p == 1)).sum()); FP = int(((y == 0) & (p == 1)).sum())
    FN = int(((y == 1) & (p == 0)).sum()); TN = int(((y == 0) & (p == 0)).sum())
    out = cls_metrics(TP, FP, FN, TN)
    assert out["accuracy"] == pytest.approx(metrics.accuracy_score(y, p)), "accuracy differs from sklearn."
    assert out["precision"] == pytest.approx(metrics.precision_score(y, p)), "precision differs from sklearn."
    assert out["recall"] == pytest.approx(metrics.recall_score(y, p)), "recall differs from sklearn."
    assert out["f1"] == pytest.approx(metrics.f1_score(y, p)), "F1 differs from sklearn."


def test_negative_counts():
    with pytest.raises(ValueError):
        cls_metrics(-1, 0, 0, 0)
