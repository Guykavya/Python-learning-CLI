import numpy as np
import pytest

from solution import seed_spread


def test_worked_example():
    vals = [0.76, 0.78, 0.75, 0.79, 0.77]
    out = seed_spread(lambda s: vals[s], range(5))
    assert out["mean"] == pytest.approx(0.77) and out["min"] == pytest.approx(0.75) and out["max"] == pytest.approx(0.79), "mean, min and max of the five scores."
    assert out["std"] == pytest.approx(np.std(vals, ddof=1)), "sample standard deviation (ddof=1)."
    assert out["n"] == 5 and isinstance(out["n"], int), "n is the number of runs."


def test_each_seed_is_run_once():
    called = []
    seed_spread(lambda s: called.append(s) or 0.5 + 0.01 * s, [3, 1, 4])
    assert called == [3, 1, 4], "call run once per seed, in the given order."


def test_one_seed_is_not_enough():
    with pytest.raises(ValueError):
        seed_spread(lambda s: 0.5, [0])
