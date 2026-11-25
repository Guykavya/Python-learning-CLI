import math

import numpy as np
import pytest

from solution import grad_f


def _f(p):
    return p[0] ** 2 * p[1] + 3 * p[1]


def test_worked_value():
    assert grad_f([1, 2]) == pytest.approx([4, 4]), "df/dx = 2xy = 4 and df/dy = x^2 + 3 = 4 at (1, 2)."


def test_matches_numerical_gradient_on_random_points():
    rng = np.random.default_rng(27)
    for _ in range(20):
        p = rng.normal(size=2) * 2
        num = np.array([(_f(p + e) - _f(p - e)) / 2e-6 for e in (np.array([1e-6, 0]), np.array([0, 1e-6]))])
        assert grad_f(p) == pytest.approx(num, rel=1e-5, abs=1e-5), f"at {np.round(p, 2)}: df/dx = 2xy, df/dy = x^2 + 3."


def test_returns_array_of_two_in_the_right_order():
    g = grad_f([0, 5])
    assert np.shape(g) == (2,), "return the two partial derivatives."
    assert g == pytest.approx([0, 3]), "at (0, 5): df/dx = 0 and df/dy = 3, in the order [df/dx, df/dy]."


def test_gradient_vanishes_nowhere_here():
    assert np.linalg.norm(grad_f([0, 0])) == pytest.approx(3.0), "df/dy = x^2 + 3 never reaches 0."
