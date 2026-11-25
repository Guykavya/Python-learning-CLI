import numpy as np
from solution import power
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize


def test_no_effect_is_the_false_alarm_rate():
    pw = power(0.10, 0.10, 1000, 2000, np.random.default_rng(1))
    assert 0.02 <= pw <= 0.09, f"With p1 = p0 the share of detections is about alpha = 0.05; you got {pw}."


def test_power_grows_with_n():
    p = [power(0.10, 0.115, n, 1500, np.random.default_rng(2)) for n in (500, 2000, 8000)]
    assert p[0] < p[1] < p[2], f"More data, more power: {p}."


def test_close_to_statsmodels():
    for n in (1000, 4000):
        mine = power(0.10, 0.115, n, 2000, np.random.default_rng(3))
        ref = NormalIndPower().power(proportion_effectsize(0.115, 0.10), n, 0.05)
        assert abs(mine - ref) < 0.06, f"n = {n}: simulated power {mine:.3f} vs formula {ref:.3f}."


def test_reproducible():
    assert power(0.1, 0.12, 800, 500, np.random.default_rng(9)) == power(0.1, 0.12, 800, 500, np.random.default_rng(9)), "Use only the given rng."


def test_all_zero_successes_is_not_a_detection():
    assert power(0.0, 0.0, 50, 100, np.random.default_rng(0)) == 0.0, "pp = 0 means SE = 0: not a detection, and no division by zero."


def test_huge_effect():
    assert power(0.1, 0.5, 200, 300, np.random.default_rng(0)) > 0.99, "A huge effect with 200 per group is detected almost always."
