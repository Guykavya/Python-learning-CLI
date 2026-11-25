import numpy as np


def pairwise_distances(a, b):
    """(n, d) and (m, d) -> (n, m) Euclidean distances."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape[1] != b.shape[1]:
        raise ValueError(f"points have {a.shape[1]} and {b.shape[1]} coordinates")
    diff = a[:, None, :] - b[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=-1))
