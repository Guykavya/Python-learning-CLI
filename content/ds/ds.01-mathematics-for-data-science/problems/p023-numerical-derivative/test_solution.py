import math

import numpy as np
import pytest

from solution import num_deriv


def test_cube():
    assert num_deriv(lambda x: x ** 3, 2.0) == pytest.approx(12.0, abs=1e-6), "d/dx x^3 = 3 x^2 = 12 at x = 2 (central difference, divide by 2h)."


def test_sin_and_exp():
    assert num_deriv(math.sin, 0.0) == pytest.approx(1.0, abs=1e-6), "cos(0) = 1."
    assert num_deriv(math.sin, 1.0) == pytest.approx(math.cos(1.0), abs=1e-6), "d/dx sin x = cos x."
    assert num_deriv(math.exp, 1.5) == pytest.approx(math.exp(1.5), abs=1e-6), "exp is its own derivative."


def test_forward_difference_is_not_good_enough():
    assert abs(num_deriv(lambda x: x ** 3, 2.0) - 12.0) < 1e-6, "forward differences are off by about h * f''(x) / 2 = 6e-5 here: use both sides."


def test_step_argument_is_used():
    coarse = num_deriv(lambda x: x ** 3, 2.0, h=0.5)
    assert coarse == pytest.approx(12.25), "with h = 0.5 the central difference of x^3 at 2 is 12 + h^2 = 12.25: use the h you are given."


def test_negative_slope_and_constant():
    assert num_deriv(lambda x: -3 * x + 1, 5.0) == pytest.approx(-3.0), "a line has the same slope everywhere."
    assert num_deriv(lambda x: 7.0, 1.0) == pytest.approx(0.0), "a constant has slope 0."
