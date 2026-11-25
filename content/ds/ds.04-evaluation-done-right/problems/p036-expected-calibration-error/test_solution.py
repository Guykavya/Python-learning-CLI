import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

from solution import ece


def test_worked_example():
    assert ece([0, 0, 1, 1, 1], [0.05, 0.15, 0.12, 0.95, 0.91], 10) == pytest.approx(0.184), "(0.05*1 + 0.365*2 + 0.07*2) / 5: weight each bin's gap by its size."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_calibrated_probabilities_have_small_ece(seed):
    rng = np.random.default_rng(seed)
    p = rng.random(20000)
    y = (rng.random(20000) < p).astype(int)
    assert ece(y, p) < 0.02, "a perfectly calibrated simulation has an ECE near 0."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_squashed_probabilities_have_large_ece_but_same_auc(seed):
    rng = np.random.default_rng(seed)
    p = rng.random(20000)
    y = (rng.random(20000) < p).astype(int)
    squashed = 0.5 + 0.3 * (p - 0.5)
    assert ece(y, squashed) > 0.1, "probabilities pulled towards 0.5 are badly calibrated."
    assert roc_auc_score(y, squashed) == pytest.approx(roc_auc_score(y, p)), "sanity check: squashing keeps the order, so AUC does not notice."
