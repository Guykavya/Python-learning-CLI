import numpy as np


def top_k(x, k):
    """Positions of the k largest values of x, best first."""
    x = np.asarray(x)
    if k < 0:
        raise ValueError(f"k must be at least 0, got {k}")
    k = min(k, x.size)
    if k == 0:
        return np.array([], dtype=np.intp)
    idx = np.argpartition(x, -k)[-k:]
    return idx[np.argsort(x[idx])[::-1]]
