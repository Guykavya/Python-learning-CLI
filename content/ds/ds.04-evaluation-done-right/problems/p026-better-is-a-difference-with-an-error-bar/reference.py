import numpy as np
from sklearn.metrics import roc_auc_score


def paired_difference(y, p_model, p_base, reps=500, seed=0):
    y = np.asarray(y)
    p_model = np.asarray(p_model)
    p_base = np.asarray(p_base)
    rng = np.random.default_rng(seed)
    n = len(y)
    diffs = []
    for _ in range(reps):
        idx = rng.integers(0, n, n)
        if len(np.unique(y[idx])) < 2:
            continue
        diffs.append(roc_auc_score(y[idx], p_model[idx]) - roc_auc_score(y[idx], p_base[idx]))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(np.mean(diffs)), float(lo), float(hi)
