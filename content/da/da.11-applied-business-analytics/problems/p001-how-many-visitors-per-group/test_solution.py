import numpy as np
import pandas as pd
import pytest

import statsmodels.api as sm

from solution import n_per_group


@pytest.mark.parametrize("mde,expected", [(0.010, 9541), (0.007, 19052), (0.005, 36792), (0.003, 100672)])
def test_the_chapters_four_cases(mde, expected):
    got = n_per_group(0.06, mde)
    assert got == expected, f"from 6%, detecting +{mde * 100:.1f} points needs {expected:,} per group, got {got:,} (round UP, use p_bar = (p0 + p1) / 2)."


def test_other_baselines_and_settings():
    assert n_per_group(0.03, 0.005) == 19744, "a lower baseline (3%) needs fewer visitors: 19,744."
    assert n_per_group(0.10, 0.02, alpha=0.05, power=0.90) == 5144, "alpha and power are parameters: 5,144 for power 0.90."


def test_close_to_statsmodels():
    for p0, mde in [(0.06, 0.005), (0.20, 0.03), (0.02, 0.004)]:
        ref = sm.stats.NormalIndPower().solve_power(effect_size=sm.stats.proportion_effectsize(p0 + mde, p0), alpha=0.05, power=0.8, ratio=1)
        assert abs(n_per_group(p0, mde) - ref) / ref < 0.02, f"p0={p0}, mde={mde}: should be within 2% of statsmodels ({ref:.0f})."


def test_returns_a_plain_int_and_halving_quadruples():
    n = n_per_group(0.06, 0.01)
    assert type(n) is int, "return a plain int."
    assert 3.8 < n_per_group(0.06, 0.005) / n < 4.2, "half the effect needs about four times the visitors."


@pytest.mark.parametrize("args", [(0.06, 0.0), (0.06, -0.01), (0.0, 0.01), (0.99, 0.02)])
def test_bad_inputs(args):
    with pytest.raises(ValueError, match="need 0 < p0 and 0 < mde and p0 \\+ mde < 1"):
        n_per_group(*args)
