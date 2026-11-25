import numpy as np
import pytest

from solution import simple_fit


def test_worked_example():
    b0, b1 = simple_fit([1, 2, 3, 4], [2, 3, 5, 6])
    assert b0 == pytest.approx(0.5), "intercept = mean_y - slope * mean_x = 4 - 1.4 * 2.5 = 0.5. Return (intercept, slope) in that order."
    assert b1 == pytest.approx(1.4), "slope = Sxy / Sxx = 7 / 5 = 1.4."


def test_flat_y_gives_zero_slope():
    b0, b1 = simple_fit([1, 2, 3], [5, 5, 5])
    assert b1 == pytest.approx(0.0, abs=1e-12), "if y never changes the slope is 0."
    assert b0 == pytest.approx(5.0), "the line is y = 5."


def test_matches_polyfit_on_random_data():
    rng = np.random.default_rng(4)
    for _ in range(10):
        x = rng.normal(size=25)
        y = 3 - 2 * x + rng.normal(size=25)
        slope, intercept = np.polyfit(x, y, 1)
        b0, b1 = simple_fit(x, y)
        assert b1 == pytest.approx(slope, rel=1e-9), "slope differs from np.polyfit. Use the same divisor in numerator and denominator (np.cov and np.var use different ones)."
        assert b0 == pytest.approx(intercept, rel=1e-9, abs=1e-12), "intercept differs from np.polyfit."


def test_returns_python_floats():
    b0, b1 = simple_fit([1, 2, 3], [2, 4, 7])
    assert isinstance(b0, float) and isinstance(b1, float), "return plain floats (use float(...))."


def test_constant_x_raises():
    with pytest.raises(ValueError, match="no spread"):
        simple_fit([2, 2, 2], [1, 2, 3])
