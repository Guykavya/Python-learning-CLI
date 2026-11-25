import math

import numpy as np
import pytest

from solution import p_shared_birthday, simulate_birthday


def test_the_famous_number():
    assert p_shared_birthday(23) == pytest.approx(0.5073, abs=1e-4), "with 23 people the chance is just over one half."
    assert p_shared_birthday(1) == 0.0, "one person cannot share with anyone."
    assert p_shared_birthday(2) == pytest.approx(1 / 365), "two people: 1/365."


def test_extremes_and_monotone():
    assert p_shared_birthday(366) == 1.0, "pigeonhole: 366 people must include a repeat."
    vals = [p_shared_birthday(k) for k in range(1, 60)]
    assert vals == sorted(vals), "more people can only raise the chance."
    assert p_shared_birthday(57) > 0.99, "57 people: above 99%."


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_simulation_is_close_to_the_formula(seed):
    est = simulate_birthday(23, 20000, seed)
    assert est == pytest.approx(p_shared_birthday(23), abs=0.02), f"simulated {est:.3f}, exact {p_shared_birthday(23):.3f}: count groups with at least one repeated day."


def test_same_seed_gives_same_estimate():
    assert simulate_birthday(30, 2000, 5) == simulate_birthday(30, 2000, 5), "use np.random.default_rng(seed)."


def test_simulation_for_a_tiny_group():
    est = simulate_birthday(2, 40000, 6)
    assert est == pytest.approx(1 / 365, abs=0.003), "two people: about 0.27% of the groups share a birthday."
