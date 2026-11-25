import inspect

import numpy as np
import pytest

from solution import best_threshold

GRID = np.round(np.arange(0.02, 0.99, 0.01), 2)


def test_signature_has_no_test_data():
    assert list(inspect.signature(best_threshold).parameters) == ["y_val", "p_val", "cost", "grid"], "exactly the four parameters (y_val, p_val, cost, grid): the threshold is chosen without the test set."


def test_small_example():
    y = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0]
    p = [0.9, 0.6, 0.4, 0.35, 0.2, 0.55, 0.1, 0.65, 0.3, 0.8]
    assert best_threshold(y, p, {"fp": 5, "fn": 100}, [0.3, 0.5, 0.7]) == pytest.approx(0.3), "costs 25, 115, 205: the cheapest is 0.3."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_calibrated_probabilities_give_the_theoretical_threshold(seed):
    rng = np.random.default_rng(seed)
    p = rng.random(20000)
    y = (rng.random(20000) < p).astype(int)
    t = best_threshold(y, p, {"fp": 20, "fn": 100}, GRID)
    assert abs(t - 20 / 120) < 0.04, f"threshold {t}: with calibrated probabilities the best threshold is near fp / (fp + fn) = 0.167."


def test_true_positive_cost_counts():
    rng = np.random.default_rng(3)
    p = rng.random(20000)
    y = (rng.random(20000) < p).astype(int)
    t = best_threshold(y, p, {"fp": 20, "tp": 20, "fn": 100}, GRID)
    assert abs(t - 0.2) < 0.04, f"threshold {t}: if every call costs 20 (also for a churner), call when p * 100 > 20, i.e. p > 0.2."


def test_first_threshold_wins_a_tie():
    assert best_threshold([1, 0], [0.9, 0.1], {"fp": 1, "fn": 1}, [0.2, 0.5, 0.8]) == pytest.approx(0.2), "all three thresholds cost 0: return the first."
