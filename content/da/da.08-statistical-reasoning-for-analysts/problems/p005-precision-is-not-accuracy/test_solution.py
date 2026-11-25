import numpy as np
import pytest
from solution import bias_spread_rmse


def test_hand_example():
    b, s, r = bias_spread_rmse([9, 11, 13], 10)
    assert b == pytest.approx(1.0), "bias = mean(estimates) - truth = 11 - 10."
    assert s == pytest.approx(np.sqrt(8 / 3)), "sd with ddof=0: sqrt((4 + 0 + 4) / 3) = 1.633. ddof=1 would give 2.0."
    assert r == pytest.approx(np.sqrt(11 / 3)), "rmse = sqrt(mean of squared errors) = sqrt((1 + 1 + 9) / 3)."


def test_identity_on_random_estimates():
    e = np.random.default_rng(3).normal(5.5, 2, 200)
    b, s, r = bias_spread_rmse(e, 5.0)
    assert r ** 2 == pytest.approx(b ** 2 + s ** 2), "rmse^2 must equal bias^2 + sd^2 (needs ddof=0)."


def test_precise_but_biased():
    b, s, r = bias_spread_rmse([20.0, 20.1, 19.9, 20.0], 10.0)
    assert s < 0.2 and b > 9.9 and r > 9.9, "Tiny spread, huge bias: the total error is dominated by the bias."


def test_negative_bias_keeps_its_sign():
    b, _, _ = bias_spread_rmse([1, 2, 3], 10)
    assert b == pytest.approx(-8), "Bias keeps its sign: estimates below the truth give a negative bias."
