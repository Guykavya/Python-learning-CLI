import numpy as np


def coverage(ci_fn, n, reps, seed=0):
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(reps):
        lo, hi = ci_fn(rng.normal(size=n))
        hits += lo <= 0.0 <= hi
    return hits / reps
