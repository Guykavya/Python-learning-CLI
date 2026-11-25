import numpy as np


def bootstrap_ci(x, stat, B=2000, level=0.95, rng=None):
    rng = np.random.default_rng() if rng is None else rng
    x = np.asarray(x)
    boots = np.array([stat(rng.choice(x, len(x), replace=True)) for _ in range(B)])
    a = (1 - level) / 2
    lo, hi = np.quantile(boots, [a, 1 - a])
    return float(lo), float(hi)
