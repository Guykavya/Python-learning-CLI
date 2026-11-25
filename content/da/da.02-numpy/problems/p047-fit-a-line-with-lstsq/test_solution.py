import numpy as np
import pytest

from solution import fit_line


def test_exact_line():
    got = fit_line([0, 1, 2, 3], [1, 3, 5, 7])
    assert isinstance(got, tuple) and len(got) == 2, f"return a tuple (slope, intercept), got {got!r}."
    slope, intercept = got
    assert isinstance(slope, float) and isinstance(intercept, float), (
        f"return Python floats, got {type(slope).__name__} and {type(intercept).__name__} (wrap with float()).")
    assert slope == pytest.approx(2.0, abs=1e-12) and intercept == pytest.approx(1.0, abs=1e-12), (
        f"points on y = 2x + 1 give slope 2 and intercept 1, got {got}. Is the column of ones second (X = [x, 1])?")


def test_small_example_against_polyfit():
    got = fit_line([1, 2, 3], [2, 2, 5])
    want = np.polyfit([1, 2, 3], [2, 2, 5], 1)
    np.testing.assert_allclose(got, want, rtol=1e-9, atol=1e-12, err_msg="(slope, intercept) must match np.polyfit(x, y, 1).")


def test_noisy_data_against_polyfit():
    rng = np.random.default_rng(47)
    for _ in range(15):
        n = int(rng.integers(2, 80))
        x = rng.uniform(-10, 10, n)
        y = rng.normal(3.0, 2.0) * x + rng.normal(0, 5) + rng.normal(0, 1, n)
        got = fit_line(x, y)
        np.testing.assert_allclose(got, np.polyfit(x, y, 1), rtol=1e-8, atol=1e-9,
                                   err_msg=f"n={n}: (slope, intercept) differs from np.polyfit(x, y, 1).")


def test_vertical_data_raises():
    with pytest.raises(ValueError):
        fit_line([4, 4, 4], [1, 2, 3])
    with pytest.raises(ValueError):
        fit_line(np.full(10, 2.5), np.arange(10.0))


@pytest.mark.parametrize("x, y", [([1, 2, 3], [1, 2]), ([1], [5]), ([], [])])
def test_bad_lengths_raise(x, y):
    with pytest.raises(ValueError):
        fit_line(x, y)


def test_horizontal_data_is_fine():
    slope, intercept = fit_line([1, 2, 3, 4], [7, 7, 7, 7])
    assert slope == pytest.approx(0.0, abs=1e-12) and intercept == pytest.approx(7.0), (
        "constant y is a horizontal line, slope 0: only constant x is a problem.")


def test_inputs_are_not_changed():
    x = np.array([1.0, 2.0, 4.0])
    y = np.array([2.0, 3.0, 9.0])
    kx, ky = x.copy(), y.copy()
    fit_line(x, y)
    np.testing.assert_array_equal(x, kx, err_msg="do not change x.")
    np.testing.assert_array_equal(y, ky, err_msg="do not change y.")
