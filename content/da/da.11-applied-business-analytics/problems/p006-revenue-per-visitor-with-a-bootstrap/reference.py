import numpy as np


def mean_diff_ci(a, b, n_boot=2000, seed=1):
    a, b = np.asarray(a, float), np.asarray(b, float)
    rng = np.random.default_rng(seed)
    ia = rng.integers(0, len(a), (n_boot, len(a)))
    ib = rng.integers(0, len(b), (n_boot, len(b)))
    diffs = b[ib].mean(axis=1) - a[ia].mean(axis=1)
    lo, hi = np.quantile(diffs, [0.025, 0.975])
    return float(b.mean() - a.mean()), (float(lo), float(hi))
