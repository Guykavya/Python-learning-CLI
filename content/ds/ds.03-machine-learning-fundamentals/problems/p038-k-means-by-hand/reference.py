import numpy as np


def kmeans(X, k, iters=100, seed=0, init=None):
    X = np.asarray(X, dtype=float)
    if k < 1 or k > len(X):
        raise ValueError("need 1 <= k <= number of points")
    if init is None:
        rng = np.random.default_rng(seed)
        centres = X[rng.choice(len(X), k, replace=False)].copy()
    else:
        centres = np.array(init, dtype=float)
    for _ in range(iters):
        d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)
        labels = d.argmin(axis=1)
        new = np.array([X[labels == j].mean(axis=0) if np.any(labels == j) else centres[j] for j in range(k)])
        if np.allclose(new, centres):
            break
        centres = new
    d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)
    return centres, d.argmin(axis=1), float(d.min(axis=1).sum())
