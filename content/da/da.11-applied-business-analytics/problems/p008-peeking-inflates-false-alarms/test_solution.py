import numpy as np
import pandas as pd
import pytest

import time

from solution import peeking_simulation


def test_one_look_keeps_the_promised_error_rate():
    for seed in (1, 2, 3):
        fixed, peek = peeking_simulation(n_sims=400, looks=1, seed=seed)
        assert 0.02 <= fixed <= 0.09, f"seed {seed}: with ONE look the false-positive rate must be near 5%, got {fixed:.3f}"
        assert fixed == peek, "with one look, 'any look' and 'the last look' are the same event."


def test_many_looks_inflate_it():
    for seed in (1, 2, 3):
        fixed, peek = peeking_simulation(n_sims=400, looks=14, seed=seed)
        assert peek > 0.10, f"seed {seed}: every extra look is another chance to stop on noise: {peek:.3f} should be well above 5%."
        assert peek > fixed, "stopping at any look is more error-prone than looking once at the end."


def test_reproducible_and_plain_floats():
    r1, r2 = peeking_simulation(n_sims=100, seed=9), peeking_simulation(n_sims=100, seed=9)
    assert r1 == r2, "the same seed must give the same result."
    assert all(type(v) is float for v in r1), "return plain floats."


def test_more_looks_never_reduce_the_chance_of_a_false_alarm_much():
    few = peeking_simulation(n_sims=300, looks=3, seed=4)[1]
    many = peeking_simulation(n_sims=300, looks=14, seed=4)[1]
    assert many > few, "14 looks give more false alarms than 3 looks."


def test_not_too_slow():
    t = time.perf_counter()
    peeking_simulation(n_sims=400, n_per_group=3000, looks=14, seed=0)
    assert time.perf_counter() - t < 15, "vectorise with cumulative sums instead of looping over visitors."
