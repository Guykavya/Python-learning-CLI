import math

import numpy as np
import pytest

from solution import grad_check

f = lambda p: float(p @ p)
P0 = np.array([1.0, 2.0])


def test_correct_gradient_has_tiny_error():
    err = grad_check(f, lambda p: 2 * p, P0)
    assert err < 1e-6, f"a correct gradient must give a relative error below 1e-6, got {err:.2e}."


def test_sign_flip_is_detected():
    err = grad_check(f, lambda p: -2 * p, P0)
    assert err > 1e-2, f"a gradient with the wrong sign must give a large error, got {err:.2e}."


def test_missing_factor_is_detected():
    err = grad_check(f, lambda p: p, P0)
    assert err > 1e-2, "forgetting the factor 2 (grad = p) must be caught."


def test_one_wrong_component_is_detected():
    g = lambda p: np.array([2 * p[0], 3 * p[1]])
    assert grad_check(f, g, P0) > 1e-2, "the second component is wrong: the check must look at every coordinate."


def test_input_point_is_not_changed():
    p = np.array([1.0, 2.0, 3.0])
    before = p.copy()
    grad_check(lambda q: float(q @ q), lambda q: 2 * q, p)
    assert np.array_equal(p, before), "do not modify p while stepping: use a copy."


def test_zero_gradients_do_not_divide_by_zero():
    assert grad_check(lambda q: 5.0, lambda q: np.zeros_like(q), np.array([1.0, 1.0])) == 0.0, "a constant function with zero gradient: return 0, not nan."


def test_works_on_a_non_trivial_function():
    g = lambda p: np.array([np.cos(p[0]) * p[1], np.sin(p[0])])
    assert grad_check(lambda p: np.sin(p[0]) * p[1], g, np.array([0.7, -1.3])) < 1e-6, "f = sin(x) y has gradient [cos(x) y, sin(x)]."
