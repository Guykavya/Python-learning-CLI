import pytest
from solution import wilson
from statsmodels.stats.proportion import proportion_confint


@pytest.mark.parametrize("k,n", [(10, 50), (3, 10), (130, 1000), (1, 5)])
def test_matches_statsmodels(k, n):
    assert wilson(k, n) == pytest.approx(proportion_confint(k, n, method="wilson"), abs=1e-9), "Compare with the Wilson formula in the problem."


def test_level_90():
    assert wilson(40, 100, 0.90) == pytest.approx(proportion_confint(40, 100, alpha=0.10, method="wilson"), abs=1e-9)


def test_zero_successes_has_width():
    lo, hi = wilson(0, 20)
    assert lo == 0.0 and 0.15 < hi < 0.17, "k = 0 of 20: the Wald interval would be (0, 0); Wilson gives about (0, 0.161)."


def test_all_successes_stay_inside():
    lo, hi = wilson(20, 20)
    assert hi <= 1.0 and 0.83 < lo < 0.85, "k = n: the interval must stay inside [0, 1]."


def test_inside_unit_interval():
    for k in range(0, 8):
        lo, hi = wilson(k, 7)
        assert 0.0 <= lo <= hi <= 1.0, "The Wald interval goes below 0 here; that is why we use Wilson."


@pytest.mark.parametrize("k,n", [(5, 0), (-1, 10), (11, 10)])
def test_bad_input(k, n):
    with pytest.raises(ValueError):
        wilson(k, n)
