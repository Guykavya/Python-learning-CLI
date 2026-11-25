import numpy as np
import pandas as pd
import pytest

from solution import mean_diff_ci


def revenue(rng, n, buy_rate, mean_spend):
    bought = rng.random(n) < buy_rate
    return np.where(bought, rng.gamma(4, mean_spend / 4, n), 0.0)


def test_observed_difference_and_hand_case():
    a = [0] * 9 + [100]
    b = [0] * 9 + [150]
    obs, (lo, hi) = mean_diff_ci(a, b, n_boot=500)
    assert obs == pytest.approx(5.0), "the observed difference is mean(b) - mean(a) = 15 - 10 = 5."
    assert lo <= obs <= hi, "the interval contains the observed difference."


def test_same_seed_same_answer_and_other_seed_differs():
    rng = np.random.default_rng(0)
    a, b = revenue(rng, 1500, 0.06, 800), revenue(rng, 1500, 0.07, 780)
    assert mean_diff_ci(a, b, 300, seed=4) == mean_diff_ci(a, b, 300, seed=4), "the same seed must reproduce the result exactly (use default_rng(seed))."
    assert mean_diff_ci(a, b, 300, seed=4)[1] != mean_diff_ci(a, b, 300, seed=5)[1], "a different seed gives a slightly different interval."


def test_close_to_the_normal_interval_on_zero_heavy_data():
    rng = np.random.default_rng(1)
    a, b = revenue(rng, 4000, 0.06, 800), revenue(rng, 4000, 0.07, 780)
    obs, (lo, hi) = mean_diff_ci(a, b, n_boot=1000, seed=2)
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    assert lo == pytest.approx(obs - 1.96 * se, abs=0.4 * se) and hi == pytest.approx(obs + 1.96 * se, abs=0.4 * se), (
        f"with 4,000 visitors per group the bootstrap interval is close to obs +/- 1.96 se ({obs - 1.96 * se:.2f} to {obs + 1.96 * se:.2f}), got {lo:.2f} to {hi:.2f}")
    assert lo < hi


def test_wider_with_less_data_and_plain_floats():
    rng = np.random.default_rng(2)
    a, b = revenue(rng, 4000, 0.06, 800), revenue(rng, 4000, 0.07, 780)
    _, (l1, h1) = mean_diff_ci(a, b, 300)
    _, (l2, h2) = mean_diff_ci(a[:400], b[:400], 300)
    assert h2 - l2 > h1 - l1, "fewer visitors give a wider interval."
    obs, ci = mean_diff_ci(a, b, 100)
    assert type(obs) is float and all(type(v) is float for v in ci), "return plain floats."
