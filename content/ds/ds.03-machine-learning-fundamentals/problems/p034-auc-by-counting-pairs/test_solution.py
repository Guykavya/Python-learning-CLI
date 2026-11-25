import time

import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

from solution import auc_by_pairs


def test_worked_examples():
    assert auc_by_pairs([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]) == pytest.approx(0.75), "3 of the 4 (positive, negative) pairs are won by the positive: 0.75."
    assert auc_by_pairs([0, 1], [0.5, 0.5]) == pytest.approx(0.5), "a tie counts as half a win."
    assert auc_by_pairs([0, 1], [0.1, 0.9]) == pytest.approx(1.0) and auc_by_pairs([0, 1], [0.9, 0.1]) == pytest.approx(0.0), "perfect and perfectly wrong rankings."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_sklearn_with_many_ties(seed):
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, 500)
    score = np.round(rng.normal(size=500) + 0.8 * y, 1)          # rounded: lots of tied scores
    assert auc_by_pairs(y, score) == pytest.approx(roc_auc_score(y, score), rel=1e-10), "differs from roc_auc_score: tied scores share the AVERAGE of their ranks."


def test_large_input_is_fast_and_small_in_memory():
    rng = np.random.default_rng(3)
    n = 60000
    y = rng.integers(0, 2, n)
    score = rng.normal(size=n) + 0.5 * y
    t0 = time.perf_counter()
    got = auc_by_pairs(y, score)
    elapsed = time.perf_counter() - t0
    assert got == pytest.approx(roc_auc_score(y, score), rel=1e-9), "wrong AUC on 60,000 rows."
    assert elapsed < 2.0, f"{elapsed:.1f} s: use ranks (O(n log n)); a pairwise comparison matrix is far too slow and too big."


def test_one_class_only():
    with pytest.raises(ValueError, match="both classes"):
        auc_by_pairs([1, 1, 1], [0.1, 0.2, 0.3])
    with pytest.raises(ValueError):
        auc_by_pairs([0, 0], [0.1, 0.2])


def test_random_scores_give_about_half():
    rng = np.random.default_rng(4)
    assert abs(auc_by_pairs(rng.integers(0, 2, 5000), rng.random(5000)) - 0.5) < 0.03, "scores unrelated to y: AUC about 0.5."
