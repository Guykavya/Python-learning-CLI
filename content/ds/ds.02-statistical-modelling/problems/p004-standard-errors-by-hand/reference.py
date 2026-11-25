import numpy as np


def ols_se(X, y):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, p = X.shape
    xtx = X.T @ X
    b = np.linalg.solve(xtx, X.T @ y)
    resid = y - X @ b
    sigma2 = float(resid @ resid) / (n - p)
    return np.sqrt(np.diag(sigma2 * np.linalg.inv(xtx)))
