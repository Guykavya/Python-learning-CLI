import numpy as np


def times_table(n):
    """n x n table, entry [i, j] = (i + 1) * (j + 1)."""
    k = np.arange(1, n + 1)
    return np.multiply.outer(k, k)


def pairwise_diff(a, b):
    """Table of shape (len(a), len(b)) with entry [i, j] = a[i] - b[j]."""
    return np.subtract.outer(np.asarray(a), np.asarray(b))
