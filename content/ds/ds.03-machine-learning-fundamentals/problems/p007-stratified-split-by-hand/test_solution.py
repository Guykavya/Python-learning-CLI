import numpy as np
import pytest

from solution import stratified_split

Y = np.array([0] * 90 + [1] * 7 + [2] * 3)


def test_complete_disjoint_and_sorted():
    tr, te = stratified_split(Y, 0.2, 0)
    assert sorted(np.concatenate([tr, te]).tolist()) == list(range(100)), "every index must be in exactly one of the two sets."
    assert tr.tolist() == sorted(tr.tolist()) and te.tolist() == sorted(te.tolist()), "return sorted index arrays."


def test_class_counts_in_test():
    _, te = stratified_split(Y, 0.2, 0)
    counts = np.bincount(Y[te], minlength=3).tolist()
    assert counts == [18, 1, 1], f"expected test counts [18, 1, 1] (round(0.2*m), at least 1), got {counts}."


def test_small_class_is_on_both_sides():
    tr, te = stratified_split(Y, 0.2, 3)
    assert (Y[tr] == 2).sum() >= 1 and (Y[te] == 2).sum() >= 1, "the class with 3 rows must appear in both train and test."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_shares_match_within_one_row(seed):
    rng = np.random.default_rng(seed)
    y = rng.choice([0, 1, 2, 3], size=400, p=[0.6, 0.25, 0.1, 0.05])
    tr, te = stratified_split(y, 0.25, seed)
    for c in range(4):
        m = (y == c).sum()
        assert abs((y[te] == c).sum() - 0.25 * m) <= 1.0, f"class {c}: test share must be within one row of 25% of its {m} rows."


def test_single_row_class_goes_to_training():
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2])
    tr, te = stratified_split(y, 0.5, 0)
    assert 8 in tr and 8 not in te, "a class with one row can only go to the training set."


def test_reproducible_and_seed_matters():
    a = stratified_split(Y, 0.2, 5)
    b = stratified_split(Y, 0.2, 5)
    c = stratified_split(Y, 0.2, 6)
    assert np.array_equal(a[1], b[1]), "same seed, same split."
    assert not np.array_equal(a[1], c[1]), "different seed, different split."
