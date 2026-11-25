import math

import numpy as np
import pytest

from solution import gradient_descent


def test_two_steps_on_a_parabola():
    w, hist = gradient_descent(lambda w: 2 * (w - 3), [0.0], 0.1, 2)
    assert w == pytest.approx([1.08]), "0 -> 0.6 -> 1.08."
    assert [float(h[0]) for h in hist] == pytest.approx([0.0, 0.6, 1.08]), "history = start plus the point after every step."


def test_converges_on_a_bowl():
    target = np.array([3.0, -1.0])
    w, hist = gradient_descent(lambda w: 2 * (w - target), [0.0, 0.0], 0.1, 200)
    assert w == pytest.approx(target, abs=1e-6), "200 steps of lr 0.1 must reach the bottom of the bowl."
    assert len(hist) == 201, f"history must have steps + 1 = 201 entries, got {len(hist)}."


def test_history_entries_are_independent_copies():
    w, hist = gradient_descent(lambda w: 2 * w, [1.0, 1.0], 0.25, 3)
    assert not np.allclose(hist[0], hist[-1]), "history[0] must still be the starting point: append w.copy(), do not update in place."
    assert hist[0] == pytest.approx([1.0, 1.0]), "the first entry is the start."


def test_start_point_is_not_modified_and_zero_steps():
    w0 = np.array([1.0, 2.0])
    w, hist = gradient_descent(lambda w: w, w0, 0.5, 0)
    assert np.array_equal(w0, [1.0, 2.0]), "do not change the caller's w0."
    assert w == pytest.approx([1.0, 2.0]) and len(hist) == 1, "zero steps: the start point and a history of length 1."


def test_descent_lowers_the_function():
    f = lambda w: float(w @ w)
    w, hist = gradient_descent(lambda w: 2 * w, [4.0, -3.0], 0.1, 10)
    vals = [f(h) for h in hist]
    assert all(b < a for a, b in zip(vals, vals[1:])), "the function value must fall at every step (check the sign of the update)."
