import numpy as np


def loss_grad(w, X, y):
    return 2.0 / len(y) * (X.T @ (X @ w - y))


def fit_and_predict(X, y, X_new, lr=0.1, steps=500):
    X = np.asarray(X, dtype=float)
    X_new = np.asarray(X_new, dtype=float)
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd = np.where(sd == 0, 1.0, sd)
    A = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    w = np.zeros(A.shape[1])
    for _ in range(steps):
        w = w - lr * loss_grad(w, A, y)
    return np.column_stack([np.ones(len(X_new)), (X_new - mu) / sd]) @ w
