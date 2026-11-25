import numpy as np


def stratified_split(y, test_frac, seed):
    y = np.asarray(y)
    rng = np.random.default_rng(seed)
    test = []
    for c in np.unique(y):
        pos = np.where(y == c)[0]
        m = len(pos)
        k = round(test_frac * m)
        k = min(max(k, 1), m - 1) if m >= 2 else 0
        if k:
            test.extend(rng.choice(pos, size=k, replace=False).tolist())
    test_idx = np.sort(np.array(test, dtype=int))
    train_idx = np.setdiff1d(np.arange(len(y)), test_idx)
    return train_idx, test_idx
