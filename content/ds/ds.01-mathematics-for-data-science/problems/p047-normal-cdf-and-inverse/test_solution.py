import math

import numpy as np
import pytest

from scipy import stats

from solution import normal_cdf, normal_ppf


def test_landmarks():
    assert normal_cdf(0) == pytest.approx(0.5), "half of the mass lies below the mean."
    assert normal_cdf(1.96) == pytest.approx(0.9750021, abs=1e-6), "1.96 is the 97.5% point."
    assert normal_ppf(0.975) == pytest.approx(1.959964, abs=1e-5), "the 97.5% quantile of the standard normal."
    assert normal_ppf(0.5) == pytest.approx(0.0, abs=1e-9), "the median of the standard normal is 0."


def test_cdf_against_scipy_with_mu_and_sigma():
    for x in (-3.0, -0.5, 0.0, 1.2, 4.0):
        assert normal_cdf(x, 1.0, 2.0) == pytest.approx(stats.norm.cdf(x, 1.0, 2.0), abs=1e-12), f"standardise: (x - mu) / sigma at x = {x}."


def test_ppf_against_scipy():
    for q in (0.001, 0.025, 0.3, 0.5, 0.9, 0.999):
        assert normal_ppf(q, 10.0, 3.0) == pytest.approx(stats.norm.ppf(q, 10.0, 3.0), abs=1e-8), f"quantile q = {q} with mu = 10, sigma = 3."


def test_round_trip():
    for q in np.linspace(0.01, 0.99, 25):
        assert normal_cdf(normal_ppf(float(q))) == pytest.approx(q, abs=1e-8), "cdf(ppf(q)) must give q back."


def test_invalid_probability():
    for q in (0.0, 1.0, -0.2, 1.5):
        with pytest.raises(ValueError):
            normal_ppf(q)
