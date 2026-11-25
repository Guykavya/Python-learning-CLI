import math

import numpy as np
import pytest

from solution import norm


@pytest.fixture(autouse=True)
def _no_linalg(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("this exercise is about doing it by hand: do not call np.linalg.norm.")
    monkeypatch.setattr(np.linalg, "norm", boom)


def test_pythagoras():
    assert norm([3, 4]) == pytest.approx(5.0), "[3, 4] has length 5: square, add, then take the square root."
    assert norm([1, 1, 1, 1]) == pytest.approx(2.0), "four ones: sqrt(4) = 2."


def test_zero_vector_and_negative_entries():
    assert norm([0, 0, 0]) == 0.0, "the zero vector has length 0."
    assert norm([-3, -4]) == pytest.approx(5.0), "squaring removes the sign: do not use the plain sum."


def test_returns_float_and_accepts_arrays():
    out = norm(np.array([1.0, 2.0, 2.0]))
    assert isinstance(out, float), f"return a Python float, got {type(out).__name__}."
    assert out == pytest.approx(3.0), "sqrt(1 + 4 + 4) = 3."


def test_random_vectors_against_numpy():
    rng = np.random.default_rng(1)
    for _ in range(20):
        v = rng.normal(size=int(rng.integers(1, 30)))
        ref = float(np.sqrt((v ** 2).sum()))
        assert norm(v) == pytest.approx(ref, rel=1e-9), "random vector: sum of squares, then sqrt."
