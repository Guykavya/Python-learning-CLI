import numpy as np


def logloss_grad(w, X, y):
    X = np.asarray(X, dtype=float)
    z = X @ np.asarray(w, dtype=float)
    e = np.exp(-np.abs(z))
    p = np.where(z >= 0, 1.0 / (1.0 + e), e / (1.0 + e))
    return X.T @ (p - np.asarray(y, dtype=float)) / len(z)
