import sys
import tracemalloc

import numpy as np
import pytest

from solution import nearest_distance


def brute_force(points):
    diff = points[:, None, :] - points[None, :, :]
    d = np.sqrt((diff ** 2).sum(axis=-1))
    np.fill_diagonal(d, np.inf)
    return d.min(axis=1)


def test_the_example():
    pts = np.array([[0.0, 0.0], [3.0, 4.0], [6.0, 8.0], [0.0, 5.0]])
    got = nearest_distance(pts, chunk=3)
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.shape == (4,), f"one distance per point: shape (4,), got {got.shape}."
    assert got.dtype == np.float64, f"distances must be float64, got {got.dtype}."
    np.testing.assert_allclose(got, [5.0, np.sqrt(10), 5.0, np.sqrt(10)], rtol=1e-12,
                               err_msg="nearest OTHER point. A result of zeros means the distance of a point to itself was not ignored.")


@pytest.mark.parametrize("chunk", [1, 7, 64, 250, 1000])
def test_five_hundred_points_against_brute_force(chunk):
    pts = np.random.default_rng(37).random((500, 2))
    got = nearest_distance(pts, chunk=chunk)
    np.testing.assert_allclose(got, brute_force(pts), rtol=1e-12,
                               err_msg=(f"chunk={chunk}: differs from the brute force. If only some chunks are wrong, check the "
                                        "self-distance column: row r of the block is point start + r."))


def test_three_dimensions_and_duplicates():
    pts = np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [4.0, 6.0, 3.0]])
    got = nearest_distance(pts, chunk=2)
    np.testing.assert_allclose(got, [0.0, 0.0, 5.0], err_msg="two identical points are each other's nearest neighbour at distance 0.")


def test_bad_arguments():
    with pytest.raises(ValueError):
        nearest_distance(np.array([[1.0, 2.0]]))
    with pytest.raises(ValueError):
        nearest_distance(np.zeros((5, 2)), chunk=0)


def test_input_is_not_changed():
    pts = np.random.default_rng(3).random((20, 2))
    keep = pts.copy()
    nearest_distance(pts, chunk=6)
    np.testing.assert_array_equal(pts, keep, err_msg="do not change the caller's points.")


def test_peak_memory_follows_the_chunk():
    pts = np.random.default_rng(4).random((6000, 2))
    tracemalloc.start()
    try:
        got = nearest_distance(pts, chunk=50)
        peak = tracemalloc.get_traced_memory()[1] / 1e6
    finally:
        tracemalloc.stop()
    assert got.shape == (6000,), f"shape (6000,) expected, got {got.shape}."
    assert peak < 25, (
        f"peak memory was {peak:.0f} MB for 6,000 points with chunk=50; a block of 50 rows needs only about 5 MB per temporary. "
        "Use the chunk argument (not a fixed block size), and never build the full n x n table.")


@pytest.mark.skipif(sys.platform == "win32", reason="Windows has no memory cap in the runner; the tracemalloc test covers chunking there.")
def test_twelve_thousand_points():
    pts = np.random.default_rng(2037).random((12_000, 2))
    try:
        got = nearest_distance(pts)
    except MemoryError:
        pytest.fail("MemoryError on 12,000 points: the full table does not fit in 1 GiB. Process chunk rows at a time (Ch. 17.4).")
    assert got.shape == (12_000,), f"shape (12000,) expected, got {got.shape}."
    assert np.all(got > 0), "random points never coincide here: every nearest distance is positive (self-distance not ignored?)."
    sample = np.random.default_rng(5).choice(12_000, size=200, replace=False)
    d = np.sqrt(((pts[sample][:, None, :] - pts[None, :, :]) ** 2).sum(axis=-1))
    d[np.arange(200), sample] = np.inf
    np.testing.assert_allclose(got[sample], d.min(axis=1), rtol=1e-12, err_msg="12,000 points: wrong nearest distance for sampled points.")
