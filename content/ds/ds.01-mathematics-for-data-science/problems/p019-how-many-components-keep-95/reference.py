import numpy as np


def components_for(X, share):
    X = np.asarray(X, dtype=float)
    Xc = X - X.mean(axis=0)
    s = np.linalg.svd(Xc, compute_uv=False)
    cum = np.cumsum(s ** 2) / np.sum(s ** 2)
    return int(np.argmax(cum >= share - 1e-12)) + 1
