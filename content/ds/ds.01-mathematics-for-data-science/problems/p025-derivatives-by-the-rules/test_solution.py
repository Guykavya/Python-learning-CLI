import math

import numpy as np
import pytest

from solution import derivative_of

FUNCS = {
    "poly": lambda x: x ** 3 - 2 * x,
    "exp2x": lambda x: math.exp(2 * x),
    "log": lambda x: math.log(x),
    "sigmoid": lambda x: 1 / (1 + math.exp(-x)),
    "product": lambda x: x * math.sin(x),
    "chain": lambda x: math.sin(x ** 2),
}
HINTS = {
    "poly": "power rule: 3x^2 - 2.",
    "exp2x": "chain rule: the inner function 2x contributes a factor 2.",
    "log": "d/dx log x = 1/x.",
    "sigmoid": "s' = s (1 - s).",
    "product": "product rule: sin x + x cos x.",
    "chain": "chain rule: the inner function x^2 contributes a factor 2x.",
}


def _num(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


@pytest.mark.parametrize("name", list(FUNCS))
def test_against_the_numerical_derivative(name):
    xs = np.linspace(0.3, 2.5, 20)
    for x in xs:
        got = derivative_of(name)(float(x))
        want = _num(FUNCS[name], float(x))
        assert got == pytest.approx(want, rel=1e-5, abs=1e-6), f"{name} at x = {x:.2f}: {HINTS[name]}"


def test_two_values_by_hand():
    assert derivative_of("poly")(2.0) == pytest.approx(10.0), "3 * 4 - 2 = 10."
    assert derivative_of("log")(4.0) == pytest.approx(0.25), "1 / 4."
    assert derivative_of("sigmoid")(0.0) == pytest.approx(0.25), "s(0) = 0.5, so s' = 0.5 * 0.5."


def test_unknown_name():
    with pytest.raises(KeyError):
        derivative_of("tangent")
