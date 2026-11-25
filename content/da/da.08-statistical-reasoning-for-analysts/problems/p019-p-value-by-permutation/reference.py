import numpy as np


def permutation_p(a, b, reps, rng):
    a, b = np.asarray(a, float), np.asarray(b, float)
    pool = np.concatenate([a, b])
    n = len(a)
    d_obs = abs(a.mean() - b.mean())
    count = 0
    for _ in range(reps):
        s = rng.permutation(pool)
        if abs(s[:n].mean() - s[n:].mean()) >= d_obs - 1e-12:
            count += 1
    return (1 + count) / (reps + 1)
