import numpy as np
import pytest

from conftest import make_curve, poly_model
from solution import bias_variance


@pytest.fixture(scope="module")
def table():
    return {d: bias_variance(d, reps=120, seed=1000) for d in (1, 3, 9)}


def test_a_line_has_high_bias_low_variance(table):
    b, v = table[1]
    assert b > 0.10, f"bias^2 of a straight line vs a sine is about 0.16, got {b:.3f}. Compare the MEAN prediction with sin(2*pi*x), not with noisy y."
    assert v < 0.08, f"a straight line barely changes from sample to sample; variance {v:.3f} is too large."


def test_degree_three_is_about_right(table):
    b, v = table[3]
    assert b < 0.02, f"degree 3 can follow one sine period: bias^2 should be near 0.003, got {b:.3f}."
    assert v < 0.05, "and its variance is small."


def test_high_degree_has_high_variance(table):
    b, v = table[9]
    assert b < 0.05, "degree 9 can follow a sine, so its bias is small."
    assert v > 4 * table[3][1], f"degree 9 variance ({v:.3f}) must be several times that of degree 3 ({table[3][1]:.3f}): use a fresh training set in every repetition."


def test_bias_falls_and_variance_rises_with_degree(table):
    assert table[1][0] > table[3][0], "bias^2 falls from degree 1 to 3."
    assert table[9][1] > table[3][1] > 0, "variance rises from degree 3 to 9."


def test_exact_values_for_degree_three():
    b, v = bias_variance(3, n_train=30, reps=40, noise=0.3, seed=500)
    pts = np.linspace(0.05, 0.95, 19)
    P = np.array([poly_model(3).fit(*make_curve(30, 0.3, seed=500 + r)).predict(pts.reshape(-1, 1)) for r in range(40)])
    assert b == pytest.approx(np.mean((P.mean(0) - np.sin(2 * np.pi * pts)) ** 2), rel=1e-8), "bias2: the training set of repetition r is make_curve(n_train, noise, seed=seed + r)."
    assert v == pytest.approx(np.mean(P.var(0)), rel=1e-8), "variance: mean over the 19 points of the population variance (ddof=0) across repetitions."
