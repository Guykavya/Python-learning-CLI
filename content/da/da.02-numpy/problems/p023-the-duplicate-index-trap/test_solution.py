from collections import Counter

import numpy as np
import pytest

from solution import add_amounts, count_by_index


def test_duplicates_are_counted():
    got = count_by_index(np.array([0, 0, 1]), 3)
    assert got.tolist() != [1, 1, 0], (
        "got [1, 1, 0]: that is exactly what counts[idx] += 1 gives (measured on NumPy 2.5.4). "
        "It reads counts[idx] once, adds 1, and writes back, so duplicate positions overwrite each other. "
        "Use np.add.at or np.bincount (Ch. 9.5).")
    assert got.tolist() == [2, 1, 0], f"expected [2, 1, 0], got {got.tolist()}."


def test_count_length_and_dtype():
    got = count_by_index(np.array([1, 1, 1]), 5)
    assert got.shape == (5,), f"one count per product: shape (5,), got {got.shape}. np.bincount needs minlength=n."
    assert np.issubdtype(got.dtype, np.integer), f"counts are whole numbers, got dtype {got.dtype}."
    assert got.tolist() == [0, 3, 0, 0, 0], f"got {got.tolist()}."


def test_count_empty():
    got = count_by_index(np.array([], dtype=np.int64), 4)
    assert got.tolist() == [0, 0, 0, 0], "no sales: four zeros."


def test_example_amounts():
    totals = np.zeros(3)
    got = add_amounts(totals, np.array([2, 0, 2]), np.array([5.0, 1.0, 4.0]))
    assert got.tolist() != [1.0, 0.0, 4.0], (
        "got [1.0, 0.0, 4.0]: out[idx] += amounts kept only the LAST amount for product 2. Use np.add.at(out, idx, amounts).")
    assert got.tolist() == [1.0, 0.0, 9.0], f"expected [1.0, 0.0, 9.0], got {got.tolist()}."


def test_amounts_start_from_totals_and_do_not_change_them():
    totals = np.array([10.0, 20.0, 30.0])
    got = add_amounts(totals, np.array([1, 1]), np.array([0.5, 0.25]))
    assert got.tolist() == [10.0, 20.75, 30.0], f"start from totals and add every amount: got {got.tolist()}."
    assert totals.tolist() == [10.0, 20.0, 30.0], "totals changed: work on totals.copy()."


def test_amounts_empty():
    got = add_amounts(np.array([1.0, 2.0]), np.array([], dtype=np.int64), np.array([]))
    assert got.tolist() == [1.0, 2.0], "no sales: the totals unchanged."


@pytest.mark.parametrize("seed", range(6))
def test_random_against_a_loop(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(1, 12))
    idx = rng.integers(0, n, size=int(rng.integers(0, 200)))
    amounts = np.round(rng.uniform(1, 50, size=len(idx)), 2)
    c = Counter(idx.tolist())
    assert count_by_index(idx, n).tolist() == [c[p] for p in range(n)], "counts differ from a Counter over idx."
    want = [0.0] * n
    for p, a in zip(idx.tolist(), amounts.tolist()):
        want[p] += a
    np.testing.assert_allclose(add_amounts(np.zeros(n), idx, amounts), want, rtol=1e-12,
                               err_msg="totals differ from a loop that adds every sale.")
