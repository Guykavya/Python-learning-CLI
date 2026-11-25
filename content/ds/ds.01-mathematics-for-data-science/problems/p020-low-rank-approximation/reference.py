import numpy as np


def low_rank(M, k):
    U, s, Vt = np.linalg.svd(np.asarray(M, dtype=float), full_matrices=False)
    return (U[:, :k] * s[:k]) @ Vt[:k]
