import numpy as np


def pca(X, k):
    X = np.asarray(X, dtype=float)
    Xc = X - X.mean(axis=0)
    C = Xc.T @ Xc / (len(X) - 1)
    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    return V[:, order[:k]].T, w[order[:k]] / w.sum()
