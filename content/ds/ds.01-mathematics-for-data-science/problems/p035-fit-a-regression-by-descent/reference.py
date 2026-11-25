import numpy as np


def fit_linear_gd(X, y, lr, steps):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    A = np.column_stack([np.ones(len(X)), X])
    w = np.zeros(A.shape[1])
    for _ in range(steps):
        w = w - lr * 2.0 / len(y) * (A.T @ (A @ w - y))
    return w
