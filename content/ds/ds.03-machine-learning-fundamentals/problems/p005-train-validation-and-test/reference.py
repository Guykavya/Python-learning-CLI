import numpy as np


def three_way_split(X, y, val=0.2, test=0.2, seed=0):
    if val + test >= 1:
        raise ValueError("val + test must be below 1")
    X = np.asarray(X)
    y = np.asarray(y)
    n = len(X)
    idx = np.random.default_rng(seed).permutation(n)
    n_test = round(n * test)
    n_val = round(n * val)
    test_idx = idx[:n_test]
    val_idx = idx[n_test:n_test + n_val]
    train_idx = idx[n_test + n_val:]
    return X[train_idx], X[val_idx], X[test_idx], y[train_idx], y[val_idx], y[test_idx]
