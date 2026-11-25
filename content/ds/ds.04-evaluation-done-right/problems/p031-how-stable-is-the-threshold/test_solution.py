import numpy as np
import pytest

from solution import threshold_stability

GRID = np.round(np.arange(0.02, 0.99, 0.01), 2)
COST = {"fp": 20, "fn": 100}


def sim(n, seed):
    rng = np.random.default_rng(seed)
    p = rng.random(n)
    return (rng.random(n) < p).astype(int), p


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_range_contains_the_theoretical_threshold(seed):
    y, p = sim(2000, seed)
    lo, hi = threshold_stability(y, p, COST, GRID, reps=60, seed=seed)
    assert lo <= 20 / 120 <= hi, f"range ({lo:.2f}, {hi:.2f}) should contain the theoretical 0.167."
    assert lo < hi, "a bootstrap of 2,000 rows does not give the same threshold every time."


def test_more_data_narrows_the_range():
    y, p = sim(600, 4)
    lo_s, hi_s = threshold_stability(y, p, COST, GRID, reps=60, seed=1)
    y, p = sim(12000, 4)
    lo_l, hi_l = threshold_stability(y, p, COST, GRID, reps=60, seed=1)
    assert hi_l - lo_l < hi_s - lo_s, "the threshold is estimated more precisely with more validation rows."


def test_reproducible():
    y, p = sim(500, 5)
    assert threshold_stability(y, p, COST, GRID, reps=20, seed=3) == threshold_stability(y, p, COST, GRID, reps=20, seed=3), "same seed, same range."
