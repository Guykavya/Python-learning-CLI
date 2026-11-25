import numpy as np


def fit_logit(X, y, max_iter=50, tol=1e-10):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    b = np.zeros(X.shape[1])
    for _ in range(max_iter):
        p = 1.0 / (1.0 + np.exp(-(X @ b)))
        grad = X.T @ (y - p)
        hess = X.T @ (X * (p * (1.0 - p))[:, None])
        step = np.linalg.solve(hess, grad)
        b = b + step
        if np.max(np.abs(step)) < tol:
            break
    return b
