import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from solution import pairwise_distances

HERE = Path(__file__).parent


def loop_distances(a, b):
    return [[math.dist(p, q) for q in b] for p in a]


def test_the_example():
    a = np.array([[0.0, 0.0], [3.0, 4.0]])
    b = np.array([[0.0, 0.0], [6.0, 8.0], [0.0, 5.0]])
    got = pairwise_distances(a, b)
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.shape == (2, 3), f"n = 2 points in a and m = 3 in b give shape (2, 3), got {got.shape}. Summed over the wrong axis?"
    assert got.dtype == np.float64, f"the distances must be float64, got {got.dtype}."
    np.testing.assert_allclose(got, [[0.0, 10.0, 5.0], [5.0, 5.0, math.sqrt(10)]], rtol=1e-12,
                               err_msg="entry [i, j] is the distance from a[i] to b[j]: square the differences, sum over the LAST axis, sqrt.")


def test_small_random_sets_match_a_loop():
    rng = np.random.default_rng(33)
    for _ in range(20):
        n, m, d = int(rng.integers(1, 8)), int(rng.integers(1, 8)), int(rng.integers(1, 5))
        a = rng.normal(0, 10, size=(n, d))
        b = rng.normal(0, 10, size=(m, d))
        got = pairwise_distances(a, b)
        assert got.shape == (n, m), f"a has shape {a.shape}, b has {b.shape}: result shape must be ({n}, {m}), got {got.shape}."
        np.testing.assert_allclose(got, loop_distances(a.tolist(), b.tolist()), rtol=1e-9, atol=1e-9,
                                   err_msg="the table differs from a plain double loop with math.dist.")


def test_identical_points_give_exact_zero():
    rng = np.random.default_rng(1)
    a = rng.normal(1e3, 1.0, size=(50, 3))
    got = pairwise_distances(a, a)
    assert not np.isnan(got).any(), ("nan in the result: with |a|^2 + |b|^2 - 2ab, rounding makes some squared distances "
                                     "slightly negative. Subtract the points, or clip at 0 before sqrt.")
    assert np.all(np.diag(got) < 1e-6), "the distance from a point to itself must be 0."
    np.testing.assert_allclose(got, got.T, atol=1e-9, err_msg="the distances of a set to itself form a symmetric table.")


def test_lists_one_point_and_one_dimension():
    got = pairwise_distances([[1, 1]], [[4, 5], [1, 1]])
    assert got.shape == (1, 2) and got.dtype == np.float64, f"lists of ints: shape (1, 2), float64; got {got.shape}, {got.dtype}."
    np.testing.assert_allclose(got, [[5.0, 0.0]], err_msg="(1, 1) to (4, 5) is 5; to itself 0.")
    got = pairwise_distances(np.array([[0.0], [2.0]]), np.array([[5.0]]))
    np.testing.assert_allclose(got, [[5.0], [3.0]], err_msg="in one dimension the distance is |a - b|.")


def test_different_dimensions_raise():
    with pytest.raises(ValueError):
        pairwise_distances(np.zeros((3, 2)), np.zeros((4, 3)))


def test_input_is_not_changed():
    a = np.array([[1.0, 2.0], [3.0, 4.0]])
    b = np.array([[0.0, 1.0]])
    keep_a, keep_b = a.copy(), b.copy()
    pairwise_distances(a, b)
    np.testing.assert_array_equal(a, keep_a, err_msg="do not change a.")
    np.testing.assert_array_equal(b, keep_b, err_msg="do not change b.")


BIG = """
import time
import numpy as np
from solution import pairwise_distances

def best_of_3(f):
    best = float("inf")
    for _ in range(3):
        t0 = time.perf_counter()
        out = f()
        best = min(best, time.perf_counter() - t0)
    return best, out

rng = np.random.default_rng(2033)
a = rng.random((2000, 3))
b = rng.random((2000, 3))
t_ref, want = best_of_3(lambda: np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(axis=-1)))
t_you, got = best_of_3(lambda: pairwise_distances(a, b))
ok = got.shape == (2000, 2000) and np.allclose(got, want, rtol=1e-9, atol=1e-9)
print("OK" if ok else "WRONG", t_you, t_ref)
"""


def test_two_thousand_points_within_the_time_budget():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=40)
    except subprocess.TimeoutExpired:
        pytest.fail("2,000 x 2,000 points did not finish in 40 seconds: looks like a Python loop: vectorise it (Ch. 12.1, Ch. 11.7).")
    assert r.returncode == 0, "your code crashed on 2,000 x 2,000 points:\n" + r.stderr[-800:]
    word, t_you, t_ref = r.stdout.split()
    assert word == "OK", "on 2,000 x 2,000 points your table differs from the broadcast version."
    t_you, t_ref = float(t_you), float(t_ref)
    assert t_you < 3 * t_ref, (
        f"your function took {t_you:.2f} s; the broadcast version took {t_ref:.2f} s on this machine (budget: 3x). "
        "Looks like a Python loop: vectorise it (Ch. 12.1, Ch. 11.7).")
