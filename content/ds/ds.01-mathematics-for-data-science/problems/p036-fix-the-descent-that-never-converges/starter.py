import numpy as np


def loss_grad(w, X, y):
    """Gradient of mean((X w - y)^2) with respect to w (this version has a bug)."""
    return 2.0 / len(y) * (X.T @ (y - X @ w))


def fit_and_predict(X, y, X_new, lr=0.1, steps=500):
    """Fit y ~ X by gradient descent, return predictions for X_new (this version blows up)."""
    A = np.column_stack([np.ones(len(X)), X])
    w = np.zeros(A.shape[1])
    for _ in range(steps):
        w = w - lr * loss_grad(w, A, y)
    return np.column_stack([np.ones(len(X_new)), X_new]) @ w
