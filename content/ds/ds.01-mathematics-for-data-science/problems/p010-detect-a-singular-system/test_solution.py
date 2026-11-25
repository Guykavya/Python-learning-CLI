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


def test_proportional_rows_are_singular():
    with pytest.raises(ValueError, match="singular"):
        solve([[1, 2], [2, 4]], [1, 2])


def test_rank_deficient_three_by_three():
    A = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    with pytest.raises(ValueError, match="singular"):
        solve(A, [1.0, 2.0, 3.0])


def test_rounding_noise_is_still_singular():
    A = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]) * 1e6
    # rounding noise leaves a pivot like 1e-10 here: compare with a tolerance relative to the matrix size, not with exactly 0.
    with pytest.raises(ValueError, match="singular"):
        solve(A, [1.0, 2.0, 3.0])


def test_a_regular_system_is_still_solved():
    assert solve([[1, 2], [3, 4]], [5, 6]) == pytest.approx([-4, 4.5]), "a non-singular system must still be solved."


def test_zero_matrix_is_singular():
    with pytest.raises(ValueError, match="singular"):
        solve(np.zeros((3, 3)), [1.0, 1.0, 1.0])


def test_a_small_but_regular_matrix_is_not_flagged():
    A = np.array([[1e-3, 0.0], [0.0, 2e-3]])
    assert solve(A, [1e-3, 2e-3]) == pytest.approx([1.0, 1.0]), "a matrix with small entries is not singular: the tolerance is relative."
