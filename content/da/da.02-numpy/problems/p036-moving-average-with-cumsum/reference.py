import numpy as np


def moving_average(x, k):
    """Mean of each window of k consecutive values; length len(x) - k + 1."""
    x = np.asarray(x, dtype=float)
    if not 1 <= k <= x.size:
        raise ValueError(f"window k={k} must be between 1 and len(x)={x.size}")
    c = np.cumsum(np.insert(x, 0, 0.0))
    return (c[k:] - c[:-k]) / k
