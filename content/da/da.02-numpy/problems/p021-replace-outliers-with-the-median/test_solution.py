import statistics

import numpy as np
import pytest

from solution import cap_outliers


def slow(values, k):
    q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    iqr = q3 - q1
    low, high = q1 - k * iqr, q3 + k * iqr
    med = statistics.median(values)
    out = [med if (v < low or v > high) else float(v) for v in values]
    return out, sum(1 for v in values if v < low or v > high)


def test_example():
    x = np.array([10, 12, 11, 13, 12, 95, 11, -40])
    cleaned, n = cap_outliers(x)
    assert n == 2, f"95 and -40 are outside the fences 8.5 and 14.5: 2 replaced, you said {n}."
    np.testing.assert_allclose(cleaned, [10, 12, 11, 13, 12, 11.5, 11, 11.5], rtol=1e-12,
                               err_msg="replace the outliers by the median of ALL values, 11.5.")


def test_result_dtype_and_shape():
    x = np.array([10, 12, 11, 13, 12, 95, 11, -40])
    cleaned, _ = cap_outliers(x)
    assert cleaned.dtype == np.float64, f"your result is {cleaned.dtype}; it must be float64 (the median 11.5 does not fit in an int array)."
    assert cleaned.shape == x.shape, f"same shape as x, got {cleaned.shape}."


def test_input_not_changed():
    x = np.array([1.0, 2.0, 3.0, 4.0, 100.0])
    before = x.copy()
    cleaned, n = cap_outliers(x)
    np.testing.assert_array_equal(x, before, err_msg="the caller's array changed: work on a copy or use np.where.")
    assert not np.shares_memory(cleaned, x), "return a new array."


def test_fence_values_are_kept():
    x = np.array([-30.0, 0.0, 0.0, 10.0, 20.0, 20.0, 50.0])
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    assert (q1 - 1.5 * iqr, q3 + 1.5 * iqr) == (-30.0, 50.0)
    cleaned, n = cap_outliers(x)
    assert n == 0, "-30 and 50 lie exactly ON the fences (q1 = 0, q3 = 20, iqr = 20): only values strictly outside are outliers (< and >, not <= and >=)."
    np.testing.assert_array_equal(cleaned, x, err_msg="nothing should change.")


def test_k_is_used():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 7.0])
    _, n_default = cap_outliers(x)
    _, n_small = cap_outliers(x, k=0.5)
    assert n_default == 0 and n_small == 1, "k scales the fences: with k = 0.5 the upper fence is 6.0 and the value 7 is outside. Did you hard-code 1.5?"


def test_median_includes_the_outliers():
    x = np.array([1.0, 2.0, 3.0, 4.0, 1000.0, 2000.0, 3.0, 2.0, 1.0])
    cleaned, n = cap_outliers(x)
    want, _ = slow(x.tolist(), 1.5)
    np.testing.assert_allclose(cleaned, want, rtol=1e-12,
                               err_msg="the replacement is np.median(x) of the ORIGINAL x, outliers included.")


@pytest.mark.parametrize("seed", range(8))
def test_random(seed):
    rng = np.random.default_rng(seed)
    x = rng.normal(50, 5, size=int(rng.integers(5, 80)))
    pos = rng.choice(len(x), size=min(3, len(x)), replace=False)
    x[pos] += rng.choice([-60, 60], size=len(pos))
    k = float(rng.choice([1.0, 1.5, 3.0]))
    want, want_n = slow(x.tolist(), k)
    cleaned, n = cap_outliers(x, k)
    assert n == want_n, f"expected {want_n} outliers for k = {k}, got {n}. Use NumPy's default (linear) percentile method."
    np.testing.assert_allclose(cleaned, want, rtol=1e-12, err_msg="cleaned values differ.")
