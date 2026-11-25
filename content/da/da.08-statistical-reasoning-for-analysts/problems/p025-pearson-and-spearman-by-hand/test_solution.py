import numpy as np
import pytest
from scipy import stats
from solution import pearson, spearman


def test_hand_values():
    assert pearson([1, 2, 3, 4, 5], [2, 4, 6, 8, 40]) == pytest.approx(0.8), "Sxy = 80, Sxx = 10, Syy = 1000: r = 80 / sqrt(10 * 1000) = 0.8."
    assert spearman([1, 2, 3, 4, 5], [2, 4, 6, 8, 40]) == pytest.approx(1.0), "The order is perfectly preserved: rho = 1."


def test_matches_scipy_random():
    rng = np.random.default_rng(0)
    x = rng.normal(size=60)
    y = 0.5 * x + rng.normal(size=60)
    assert pearson(x, y) == pytest.approx(stats.pearsonr(x, y)[0])
    assert spearman(x, y) == pytest.approx(stats.spearmanr(x, y)[0])


def test_ties_use_average_ranks():
    x = [1, 2, 2, 3, 3, 3, 7]
    y = [5, 5, 6, 9, 8, 8, 1]
    assert spearman(x, y) == pytest.approx(stats.spearmanr(x, y)[0]), "Tied values share the average of their ranks."


def test_negative_and_monotone_curve():
    x = np.arange(1, 8)
    assert pearson(x, -x) == pytest.approx(-1.0)
    assert spearman(x, x ** 3) == pytest.approx(1.0) and pearson(x, x ** 3) < 1.0, "A monotone curve: Spearman is 1, Pearson is below 1."


def test_constant_column():
    with pytest.raises(ValueError, match="r is undefined when one variable does not vary"):
        pearson([1, 2, 3], [4, 4, 4])
    with pytest.raises(ValueError, match="does not vary"):
        spearman([7, 7, 7], [1, 2, 3])


def test_bad_lengths():
    with pytest.raises(ValueError):
        pearson([1, 2, 3], [1, 2])
