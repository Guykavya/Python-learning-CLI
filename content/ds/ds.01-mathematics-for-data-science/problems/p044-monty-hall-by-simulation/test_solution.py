import math

import numpy as np
import pytest

from solution import monty_hall


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_staying_wins_a_third(seed):
    assert monty_hall(False, 20000, seed) == pytest.approx(1 / 3, abs=0.02), "staying keeps the first pick: 1/3 of the time it is the car."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_switching_wins_two_thirds(seed):
    assert monty_hall(True, 20000, seed) == pytest.approx(2 / 3, abs=0.02), "switching wins whenever the first pick was a goat: 2/3 of the time."


def test_stay_and_switch_add_up_to_one_with_the_same_seed():
    s = monty_hall(True, 5000, 7)
    t = monty_hall(False, 5000, 7)
    assert s + t == pytest.approx(1.0), "with the same random draws, switching wins exactly when staying loses."


def test_result_is_a_fraction():
    r = monty_hall(True, 100, 1)
    assert 0.0 <= r <= 1.0 and (r * 100) == pytest.approx(round(r * 100)), "return wins / trials, a number between 0 and 1."
