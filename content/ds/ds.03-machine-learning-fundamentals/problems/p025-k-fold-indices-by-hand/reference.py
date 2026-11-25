import numpy as np


def kfold_indices(n, k, seed=0):
    if k < 2 or k > n:
        raise ValueError("need 2 <= k <= n")
    idx = np.random.default_rng(seed).permutation(n)
    return np.array_split(idx, k)
