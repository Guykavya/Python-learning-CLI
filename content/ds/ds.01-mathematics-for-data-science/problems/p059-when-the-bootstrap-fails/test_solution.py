import math

import numpy as np
import pytest

from solution import boot_coverage

NORMAL = lambda rng, n: rng.normal(0.0, 1.0, n)
UNIFORM = lambda rng, n: rng.uniform(0.0, 1.0, n)


def test_the_median_is_covered_about_95_percent():
    c = boot_coverage(NORMAL, 50, np.median, 0.0, 300, 400, 0)
    assert 0.88 <= c <= 0.99, f"the percentile bootstrap of a median should cover about 95%, got {c:.3f}."


def test_the_mean_is_covered_about_95_percent():
    c = boot_coverage(NORMAL, 50, np.mean, 0.0, 300, 400, 1)
    assert 0.88 <= c <= 0.99, f"the percentile bootstrap of a mean should cover about 95%, got {c:.3f}."


def test_the_maximum_fails():
    c = boot_coverage(UNIFORM, 50, np.max, 1.0, 200, 300, 2)
    assert c < 0.7, f"a resample can never exceed the sample maximum, so the interval cannot reach the true maximum 1: coverage is far below 95% (got {c:.3f})."


def test_reproducible():
    a = boot_coverage(NORMAL, 20, np.mean, 0.0, 30, 100, 3)
    b = boot_coverage(NORMAL, 20, np.mean, 0.0, 30, 100, 3)
    assert a == b and 0.0 <= a <= 1.0, "the same seed gives the same fraction."


def test_truth_far_away_is_never_covered():
    assert boot_coverage(NORMAL, 20, np.mean, 100.0, 20, 50, 4) == 0.0, "an interval near 0 never contains 100."
