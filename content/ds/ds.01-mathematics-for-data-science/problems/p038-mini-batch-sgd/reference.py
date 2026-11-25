import numpy as np


def sgd(X, y, lr, epochs, batch, seed=0):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    rng = np.random.default_rng(seed)
    n = len(y)
    w = np.zeros(X.shape[1])
    for _ in range(epochs):
        order = rng.permutation(n)
        for start in range(0, n, batch):
            idx = order[start:start + batch]
            Xb, yb = X[idx], y[idx]
            w = w - lr * 2.0 / len(idx) * (Xb.T @ (Xb @ w - yb))
    return w
