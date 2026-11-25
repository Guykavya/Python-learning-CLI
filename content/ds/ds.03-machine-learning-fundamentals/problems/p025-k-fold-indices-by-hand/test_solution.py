import numpy as np
import pytest

from solution import kfold_indices


@pytest.mark.parametrize("n,k", [(10, 5), (11, 5), (23, 4), (7, 7), (100, 3)])
def test_partition_properties(n, k):
    folds = kfold_indices(n, k, seed=1)
    assert len(folds) == k, f"expected {k} folds."
    allidx = np.concatenate(folds)
    assert sorted(allidx.tolist()) == list(range(n)), "the folds must be disjoint and together cover 0..n-1 exactly once."
    sizes = [len(f) for f in folds]
    assert max(sizes) - min(sizes) <= 1, f"fold sizes {sizes} should differ by at most 1."


def test_eleven_rows_in_five_folds():
    assert sorted(len(f) for f in kfold_indices(11, 5, 0)) == [2, 2, 2, 2, 3], "11 rows in 5 folds: sizes 3, 2, 2, 2, 2."


def test_shuffled_and_seeded():
    a = kfold_indices(50, 5, seed=3)
    b = kfold_indices(50, 5, seed=3)
    c = kfold_indices(50, 5, seed=4)
    assert all(np.array_equal(x, y) for x, y in zip(a, b)), "same seed, same folds."
    assert not all(np.array_equal(x, y) for x, y in zip(a, c)), "different seed, different folds."
    assert not np.array_equal(a[0], np.arange(10)), "the rows must be shuffled before cutting."


def test_bad_k():
    with pytest.raises(ValueError):
        kfold_indices(10, 1)
    with pytest.raises(ValueError):
        kfold_indices(5, 6)
