import numpy as np


def cov_matrix(X):
    X = np.asarray(X, dtype=float)
    Xc = X - X.mean(axis=0)
    return Xc.T @ Xc / (len(X) - 1)
