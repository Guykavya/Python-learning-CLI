import numpy as np
import pytest
import statsmodels.api as sm

from solution import influential_points


def planted(seed):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=50)
    y = 1 + 2 * x + rng.normal(size=50)
    x = np.append(x, 6.0)          # far out in x ...
    y = np.append(y, -10.0)        # ... and far off the line: high leverage AND a big residual
    return sm.OLS(y, sm.add_constant(x)).fit()


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_planted_point_is_found_first(seed):
    got = influential_points(planted(seed))
    assert got and got[0] == 50, f"the bad point is at position 50 and has the largest Cook's distance; got {got[:5]}."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_statsmodels_ranking(seed):
    res = planted(seed)
    cooks = res.get_influence().cooks_distance[0]
    expected = [int(i) for i in np.argsort(-cooks) if cooks[i] > 4 / 51]
    assert influential_points(res) == expected, "flag D > 4/n, strictly, sorted from the largest D to the smallest."


def test_custom_threshold():
    res = planted(0)
    assert influential_points(res, threshold=1.0) == [50], "only the planted point exceeds Cook's D = 1."
    assert influential_points(res, threshold=1e9) == [], "nothing above a huge threshold: return an empty list."


def test_clean_data_flags_few_points():
    rng = np.random.default_rng(11)
    x = rng.normal(size=200)
    y = 1 + 2 * x + rng.normal(size=200)
    got = influential_points(sm.OLS(y, sm.add_constant(x)).fit())
    assert len(got) < 30, f"{len(got)} flagged out of 200: even on clean data D > 4/n flags only a modest share (about 5-10%). A far bigger list means a wrong threshold (it must be 4/n)."


def test_returns_a_list_of_ints():
    got = influential_points(planted(0))
    assert isinstance(got, list) and all(isinstance(i, int) for i in got), "return a list of plain ints."
