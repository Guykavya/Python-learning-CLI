import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

from solution import paired_difference


def scores(seed, n=1000):
    rng = np.random.default_rng(seed)
    signal = rng.normal(size=n)
    y = (signal + rng.normal(size=n) > 0).astype(int)
    base = signal + 1.5 * rng.normal(size=n)            # a weaker view of the same signal
    better = signal + 0.8 * rng.normal(size=n)          # a stronger view
    same = base + 0.001 * rng.normal(size=n)            # practically the base model
    return y, base, better, same


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_a_real_gain_excludes_zero(seed):
    y, base, better, _ = scores(seed)
    m, lo, hi = paired_difference(y, better, base, reps=200, seed=seed)
    assert lo > 0, f"interval ({lo:.3f}, {hi:.3f}): the better model's gain is real and the paired interval must stay above 0."
    assert lo < m < hi, "the mean lies inside its interval."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_a_fake_gain_includes_zero(seed):
    y, base, _, same = scores(seed)
    m, lo, hi = paired_difference(y, same, base, reps=200, seed=seed)
    assert lo <= 0 <= hi, f"interval ({lo:.4f}, {hi:.4f}): two practically identical models must not be declared different."


def test_paired_is_narrower_than_unpaired():
    y, base, better, _ = scores(5)
    _, lo, hi = paired_difference(y, better, base, reps=200, seed=1)
    rng = np.random.default_rng(1)
    n = len(y)
    unpaired = []
    for _ in range(200):
        i, j = rng.integers(0, n, n), rng.integers(0, n, n)
        unpaired.append(roc_auc_score(y[i], better[i]) - roc_auc_score(y[j], base[j]))
    assert hi - lo < np.percentile(unpaired, 97.5) - np.percentile(unpaired, 2.5), "resampling the SAME rows for both models must give a narrower interval than independent resamples."


def test_single_class_resamples_are_skipped():
    y = np.array([0] * 39 + [1])
    rng = np.random.default_rng(0)
    m, lo, hi = paired_difference(y, rng.random(40), rng.random(40), reps=200, seed=0)
    assert np.isfinite([m, lo, hi]).all(), "skip resamples with only one class instead of crashing."
