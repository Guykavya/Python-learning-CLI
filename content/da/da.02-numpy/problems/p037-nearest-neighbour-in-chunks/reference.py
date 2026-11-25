import numpy as np


def nearest_distance(points, chunk=250):
    """Distance from each point to its nearest other point, chunk rows at a time."""
    points = np.asarray(points, dtype=float)
    n = len(points)
    if n < 2:
        raise ValueError(f"need at least 2 points, got {n}")
    if chunk < 1:
        raise ValueError(f"chunk must be at least 1, got {chunk}")
    best = np.empty(n)
    for start in range(0, n, chunk):
        block = points[start:start + chunk]                            # (c, d)
        d2 = ((block[:, None, :] - points[None, :, :]) ** 2).sum(axis=-1)   # (c, n)
        rows = np.arange(len(block))
        d2[rows, start + rows] = np.inf                                # ignore self
        best[start:start + len(block)] = d2.min(axis=1)
    return np.sqrt(best)
