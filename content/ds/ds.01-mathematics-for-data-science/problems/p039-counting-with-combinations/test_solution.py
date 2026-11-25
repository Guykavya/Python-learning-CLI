import math

import numpy as np
import pytest

from solution import p_exactly_k_heads


def test_small_cases():
    assert p_exactly_k_heads(2, 1) == pytest.approx(0.5), "HT and TH out of four outcomes."
    assert p_exactly_k_heads(3, 0) == pytest.approx(0.125), "only TTT: 1 / 8."
    assert p_exactly_k_heads(10, 5) == pytest.approx(0.24609375), "252 / 1024."


def test_probabilities_sum_to_one():
    for n in (1, 7, 20, 50):
        total = sum(p_exactly_k_heads(n, k) for k in range(n + 1))
        assert total == pytest.approx(1.0), f"for n = {n} the probabilities of 0..n heads must add up to 1."


def test_out_of_range_is_zero():
    assert p_exactly_k_heads(5, 6) == 0.0 and p_exactly_k_heads(5, -1) == 0.0, "k outside 0..n has probability 0 (math.comb would raise)."


def test_symmetry_and_large_n():
    assert p_exactly_k_heads(9, 2) == pytest.approx(p_exactly_k_heads(9, 7)), "heads and tails are symmetric."
    assert p_exactly_k_heads(1000, 500) == pytest.approx(0.0252250181783608), "n = 1000 must not overflow."
