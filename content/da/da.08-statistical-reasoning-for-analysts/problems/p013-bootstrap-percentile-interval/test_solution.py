import time

import numpy as np
from scipy import stats
from solution import bootstrap_ci

X = np.random.default_rng(0).exponential(100, 200)


def test_reproducible():
    a = bootstrap_ci(X, np.mean, 500, 0.95, np.random.default_rng(4))
    b = bootstrap_ci(X, np.mean, 500, 0.95, np.random.default_rng(4))
    assert a == b, "Same seed, same interval: draw only with the rng you are given."


def test_interval_contains_the_estimate():
    for seed in range(5):
        lo, hi = bootstrap_ci(X, np.median, 1000, 0.95, np.random.default_rng(seed))
        assert lo <= np.median(X) <= hi, "The interval should contain the sample median."


def test_close_to_t_interval_for_the_mean():
    lo, hi = bootstrap_ci(X, np.mean, 3000, 0.95, np.random.default_rng(1))
    tl, th = stats.t.interval(0.95, len(X) - 1, loc=X.mean(), scale=stats.sem(X))
    assert abs((hi - lo) - (th - tl)) < 0.15 * (th - tl), "For the mean the bootstrap and t intervals have similar widths."


def test_more_data_narrower_interval():
    pop = np.random.default_rng(9).exponential(100, 50_000)
    small = np.random.default_rng(10).choice(pop, 100)
    big = np.random.default_rng(11).choice(pop, 400)
    w1 = np.subtract(*bootstrap_ci(small, np.mean, 1000, 0.95, np.random.default_rng(2))[::-1])
    w2 = np.subtract(*bootstrap_ci(big, np.mean, 1000, 0.95, np.random.default_rng(2))[::-1])
    assert 0.3 < w2 / w1 < 0.7, "4 times the data should roughly halve the width (resample WITH replacement, len(x) values each)."


def test_level_changes_width():
    w90 = np.subtract(*bootstrap_ci(X, np.mean, 1000, 0.90, np.random.default_rng(3))[::-1])
    w99 = np.subtract(*bootstrap_ci(X, np.mean, 1000, 0.99, np.random.default_rng(3))[::-1])
    assert w99 > w90, "A 99% interval is wider than a 90% interval."


def test_fast_enough():
    t0 = time.time()
    bootstrap_ci(X, np.mean, 2000, 0.95, np.random.default_rng(0))
    assert time.time() - t0 < 2.0, "B = 2000 resamples of 200 values should take well under 2 seconds."
