import math

import numpy as np
import pytest

from solution import solve


@pytest.fixture(autouse=True)
def _no_library_solver(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("this exercise is about doing it by hand: do not call np.linalg.solve / inv / lstsq.")
    for name in ("solve", "inv", "lstsq", "pinv"):
        monkeypatch.setattr(np.linalg, name, boom)


def test_small_system():
    assert solve([[2, 1], [1, 3]], [3, 5]) == pytest.approx([0.8, 1.4]), "2x + y = 3 and x + 3y = 5 give x = 0.8, y = 1.4."


def test_zero_on_the_diagonal_needs_a_swap():
    assert solve([[0, 1], [1, 0]], [4, 7]) == pytest.approx([7, 4]), "A[0][0] is 0: swap the rows (in b too) before dividing."


def test_random_systems():
    rng = np.random.default_rng(8)
    for n in (3, 5, 8):
        A = rng.normal(size=(n, n)) + n * np.eye(n)
        x_true = rng.normal(size=n)
        assert solve(A, A @ x_true) == pytest.approx(x_true, rel=1e-8), f"random {n}x{n} system: A @ x should reproduce b."


def test_inputs_are_not_modified():
    A = np.array([[0.0, 2.0], [3.0, 1.0]])
    b = np.array([4.0, 5.0])
    A0, b0 = A.copy(), b.copy()
    solve(A, b)
    assert np.array_equal(A, A0) and np.array_equal(b, b0), "work on copies: the caller's A and b must not change."


def test_integers_in_give_floats_out():
    x = solve([[2, 0], [0, 4]], [1, 1])
    assert x == pytest.approx([0.5, 0.25]), "integer input must not be floor-divided: use dtype=float."


def test_a_tiny_pivot_is_handled_by_pivoting():
    A = np.array([[1e-14, 1.0], [1.0, 1.0]])
    assert solve(A, [1.0, 2.0]) == pytest.approx(np.array([1.0, 1.0]), abs=1e-6), "swap in the row with the largest entry, or the tiny pivot ruins the answer."
