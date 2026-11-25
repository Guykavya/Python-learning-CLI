import numpy as np
import pandas as pd
import pytest

from scipy import stats

from solution import srm_check, srm_verdict


def test_matches_scipy():
    chi2, p = srm_check([12_000, 11_100])
    ref = stats.chisquare([12_000, 11_100], [11_550, 11_550])
    assert chi2 == pytest.approx(ref.statistic) and p == pytest.approx(ref.pvalue, rel=1e-6), f"chi-square against the expected counts 11,550 each: {ref.statistic:.2f}, got {chi2:.2f}"
    assert chi2 == pytest.approx(35.065, abs=1e-3)


def test_verdicts():
    assert srm_verdict([12_000, 11_100]) == "MISMATCH", "12,000 against 11,100 in a 50/50 test is a sample ratio mismatch."
    assert srm_verdict([12_010, 11_990]) == "ok", "a difference of 20 visitors is normal noise."
    assert srm_verdict([12_000, 12_000]) == "ok"


def test_uneven_planned_split():
    assert srm_verdict([6_030, 3_970], (0.6, 0.4)) == "ok", "a 60/40 plan: 6,030 / 3,970 is fine."
    assert srm_verdict([5_000, 5_000], (0.6, 0.4)) == "MISMATCH", "a 50/50 result in a planned 60/40 test is a mismatch."


def test_three_groups_and_types():
    chi2, p = srm_check([3_300, 3_350, 3_350], (1 / 3, 1 / 3, 1 / 3))
    assert type(chi2) is float and type(p) is float, "return plain floats."
    assert 0 < p < 1


def test_bad_shares():
    with pytest.raises(ValueError, match="shares must add up to 1"):
        srm_check([100, 100], (0.5, 0.6))
