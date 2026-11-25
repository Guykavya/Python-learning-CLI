import numpy as np


def mse_grad(w, X, y):
    X = np.asarray(X, dtype=float)
    w = np.asarray(w, dtype=float)
    y = np.asarray(y, dtype=float)
    return 2.0 / len(y) * (X.T @ (X @ w - y))
