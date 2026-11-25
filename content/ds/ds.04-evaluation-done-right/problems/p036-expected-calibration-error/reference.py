import numpy as np


def ece(y, p, bins=10):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    k = np.minimum(np.floor(p * bins).astype(int), bins - 1)
    total = 0.0
    for b in np.unique(k):
        m = k == b
        total += abs(y[m].mean() - p[m].mean()) * m.sum()
    return float(total / len(y))
