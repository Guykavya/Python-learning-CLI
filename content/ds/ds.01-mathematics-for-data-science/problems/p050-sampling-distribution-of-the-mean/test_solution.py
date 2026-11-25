import math

import numpy as np
import pytest

from solution import sample_means

EXP = lambda rng, shape: rng.exponential(2.0, shape)


def test_shape_and_reproducibility():
    a = sample_means(EXP, 10, 300, 1)
    assert a.shape == (300,), f"one mean per repetition: expected shape (300,), got {a.shape}."
    assert np.array_equal(a, sample_means(EXP, 10, 300, 1)), "the same seed must give the same means."
    assert not np.array_equal(a, sample_means(EXP, 10, 300, 2)), "a different seed must give different means."


@pytest.mark.parametrize("n", [4, 16, 64])
def test_spread_follows_sigma_over_root_n(n):
    means = sample_means(EXP, n, 4000, 3)
    assert means.std() == pytest.approx(2.0 / math.sqrt(n), rel=0.1), f"n = {n}: the std of the means must be sigma / sqrt(n) = {2.0 / math.sqrt(n):.3f}."
    assert means.mean() == pytest.approx(2.0, abs=0.1), "the means are centred on the true mean 2."


def test_means_become_less_skewed_as_n_grows():
    skew = lambda x: float(np.mean(((x - x.mean()) / x.std()) ** 3))
    s4 = skew(sample_means(EXP, 4, 5000, 4))
    s64 = skew(sample_means(EXP, 64, 5000, 4))
    assert s64 < s4 and s64 < 0.6, f"skewness should fall as n grows (central limit theorem), got {s4:.2f} then {s64:.2f}."


def test_works_with_another_distribution():
    uni = lambda rng, shape: rng.uniform(0, 1, shape)
    assert sample_means(uni, 25, 4000, 5).std() == pytest.approx(math.sqrt(1 / 12) / 5, rel=0.1), "uniform(0,1) has std sqrt(1/12); divide by sqrt(25)."
