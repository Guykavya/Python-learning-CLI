import numpy as np


def ridge_fit(X, y, alpha):
    if alpha < 0:
        raise ValueError("alpha must be non-negative")
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    xm, ym = X.mean(axis=0), y.mean()
    Xc, yc = X - xm, y - ym
    beta = np.linalg.solve(Xc.T @ Xc + alpha * np.eye(X.shape[1]), Xc.T @ yc)
    return float(ym - xm @ beta), beta
