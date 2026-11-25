import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import KFold

from solution import target_encode


def data(seed=0, n=300):
    rng = np.random.default_rng(seed)
    col = rng.choice([f"pc{i}" for i in range(40)], n)       # many small categories: the leak would be strong
    y = rng.integers(0, 2, n)
    test = np.array(["pc0", "pc1", "pc39", "never_seen"])
    return col, y, test


def test_a_row_never_uses_its_own_label():
    col, y, test = data()
    enc, _ = target_encode(col, y, test, 5, 0)
    for i in (0, 7, 42, 123, 299):
        y2 = y.copy()
        y2[i] = 1 - y2[i]
        enc2, _ = target_encode(col, y2, test, 5, 0)
        assert enc2[i] == pytest.approx(enc[i]), f"row {i}: flipping its own label changed its encoding. Use the mean of the OTHER folds."


def test_out_of_fold_values():
    col, y, test = data(1)
    enc, _ = target_encode(col, y, test, 5, 3)
    for fit_idx, enc_idx in KFold(5, shuffle=True, random_state=3).split(col):
        means = pd.Series(y[fit_idx]).groupby(col[fit_idx]).mean()
        for i in enc_idx[:10]:
            exp = means.get(col[i], y[fit_idx].mean())
            assert enc[i] == pytest.approx(exp), "a training row gets its category mean from the other folds (KFold(n_folds, shuffle=True, random_state=seed))."


def test_test_rows_use_all_training_rows():
    col, y, test = data(2)
    _, te = target_encode(col, y, test, 5, 0)
    full = pd.Series(y).groupby(col).mean()
    assert te[:3] == pytest.approx([full["pc0"], full["pc1"], full["pc39"]]), "test rows: the category mean over ALL training rows."
    assert te[3] == pytest.approx(y.mean()), "a category never seen in training gets the overall training mean."


def test_types_and_lengths():
    col, y, test = data(3)
    a, b = target_encode(col, y, test)
    assert a.shape == (300,) and b.shape == (4,) and a.dtype.kind == "f", "two float arrays: one value per training row and per test row."
