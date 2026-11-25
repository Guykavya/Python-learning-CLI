import numpy as np


def power_iteration(A, steps=500, seed=0):
    A = np.asarray(A, dtype=float)
    rng = np.random.default_rng(seed)
    v = rng.normal(size=A.shape[0])
    v /= np.linalg.norm(v)
    for _ in range(steps):
        w = A @ v
        v = w / np.linalg.norm(w)
    return float(v @ A @ v), v
