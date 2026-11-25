import math
import statistics

import numpy as np
import pytest

from solution import percentile


# The da.01 definitions (da.01 p021), used as the truth.
def nearest_rank(values, p):
    s = sorted(values)
    return s[max(1, math.ceil(p * len(s) / 100)) - 1]


def inclusive(values, p):
    s = sorted(values)
    pos = (len(s) - 1) * p / 100
    lo = math.floor(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def exclusive(values, p):
    s = sorted(values)
    n = len(s)
    pos = (n + 1) * p / 100
    if pos < 1 or pos > n:
        return None
    lo = math.floor(pos)
    hi = min(lo + 1, n)
    return s[lo - 1] + (s[hi - 1] - s[lo - 1]) * (pos - lo)


DATA = [15, 20, 35, 40, 50]


def test_the_example():
    got = percentile(DATA, 25)
    assert isinstance(got, float), f"return a Python float, not {type(got).__name__} (wrap the result in float())."
    assert got == 20.0, f"inclusive 25th percentile of {DATA} is 20.0 (NumPy's default 'linear'), got {got}."
    assert percentile(DATA, 25, "exclusive") == pytest.approx(17.5), "exclusive 25th percentile is 17.5: which NumPy method matches statistics' default? (Ch. 14.2)"
    assert percentile(DATA, 25, "nearest_rank") == 20.0, "nearest-rank 25th percentile: rank ceil(1.25) = 2, the value 20."


def test_against_statistics_quantiles():
    rng = np.random.default_rng(42)
    for _ in range(30):
        data = rng.normal(60, 15, size=int(rng.integers(5, 40))).round(1).tolist()
        q_inc = statistics.quantiles(data, n=4, method="inclusive")
        q_exc = statistics.quantiles(data, n=4)
        for k, p in enumerate((25, 50, 75)):
            assert percentile(data, p, "inclusive") == pytest.approx(q_inc[k], rel=1e-12), f"inclusive p={p} differs from statistics.quantiles(method='inclusive')."
            assert percentile(data, p, "exclusive") == pytest.approx(q_exc[k], rel=1e-12), f"exclusive p={p} differs from statistics.quantiles (default method)."


def test_against_the_da01_definitions():
    rng = np.random.default_rng(142)
    for _ in range(200):
        data = rng.integers(0, 100, size=int(rng.integers(1, 15))).tolist()
        p = float(rng.choice([0, 100, 1, 99, 50, 25, 75, 10, 33.3, float(rng.uniform(0, 100))]))
        want = nearest_rank(data, p)
        got = percentile(data, p, "nearest_rank")
        assert got == want, (f"nearest_rank of {sorted(data)} at p={p}: expected {want}, got {got}. "
                             "It must always be a data value: 'nearest' or 'lower' are not the same rule. Try the methods on a tiny list.")
        assert percentile(data, p, "inclusive") == pytest.approx(inclusive(data, p), rel=1e-12, abs=1e-12), f"inclusive {sorted(data)} p={p}."
        want_exc = exclusive(data, p)
        if want_exc is None:
            with pytest.raises(ValueError):
                percentile(data, p, "exclusive")
        else:
            assert percentile(data, p, "exclusive") == pytest.approx(want_exc, rel=1e-12, abs=1e-12), f"exclusive {sorted(data)} p={p}."


def test_exclusive_too_extreme_raises():
    for p in (0, 10, 90, 100):
        with pytest.raises(ValueError):
            percentile(DATA, p, "exclusive")
    assert percentile(DATA, 100 / 6, "exclusive") == pytest.approx(15.0), "position exactly 1 is allowed: the smallest value."


@pytest.mark.parametrize("args", [([], 50), (DATA, -1), (DATA, 100.5)])
def test_bad_data_or_p(args):
    with pytest.raises(ValueError):
        percentile(*args)


def test_unknown_method_is_named():
    with pytest.raises(ValueError) as info:
        percentile(DATA, 50, "median_unbiased")
    assert "median_unbiased" in str(info.value), "the message should name the method that was not understood."


def test_input_is_not_changed():
    data = [50, 15, 40, 20, 35]
    percentile(data, 50, "nearest_rank")
    assert data == [50, 15, 40, 20, 35], "do not sort the caller's list in place."
