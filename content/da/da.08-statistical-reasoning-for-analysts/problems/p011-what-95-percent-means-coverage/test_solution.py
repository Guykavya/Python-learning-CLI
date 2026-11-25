import numpy as np
from scipy import stats
from solution import coverage


def ci_mean(x, level=0.95):
    n = len(x)
    se = x.std(ddof=1) / np.sqrt(n)
    h = stats.t.ppf((1 + level) / 2, df=n - 1) * se
    return x.mean() - h, x.mean() + h


def ci_wrong(x):
    return x.mean() - 1.96 * x.std(ddof=1), x.mean() + 1.96 * x.std(ddof=1)     # sd instead of SE


def sampler(rng):
    return rng.normal(10, 2, 30)


def test_constant_interval():
    assert coverage(lambda s: (0, 1), lambda rng: rng.random(3), 0.5, 20, np.random.default_rng(0)) == 1.0
    assert coverage(lambda s: (0, 1), lambda rng: rng.random(3), 5, 20, np.random.default_rng(0)) == 0.0, "Truth outside every interval: coverage 0."


def test_share_not_count():
    c = coverage(lambda s: (0, 1), lambda rng: rng.random(3), 0.5, 7, np.random.default_rng(0))
    assert c == 1.0, "Return a share between 0 and 1 (hits / reps), not the number of hits."


def test_t_interval_covers_about_95_percent():
    c = coverage(ci_mean, sampler, 10, 1000, np.random.default_rng(1))
    assert 0.90 <= c <= 0.975, f"A 95% t interval on normal data should cover about 95% of the time, you got {c}."


def test_sd_instead_of_se_is_too_wide():
    c = coverage(ci_wrong, sampler, 10, 500, np.random.default_rng(2))
    assert c > 0.99, "Intervals made with the sd instead of the SE cover almost 100% of the time: valid but useless."


def test_uses_the_given_rng():
    a = coverage(ci_mean, sampler, 10, 200, np.random.default_rng(3))
    b = coverage(ci_mean, sampler, 10, 200, np.random.default_rng(3))
    assert a == b, "Same seed, same coverage: pass the rng to the sampler."
