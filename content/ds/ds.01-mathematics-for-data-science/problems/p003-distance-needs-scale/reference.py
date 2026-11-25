import numpy as np


def standardise(X):
    X = np.asarray(X, dtype=float)
    std = X.std(axis=0)
    std = np.where(std == 0, 1.0, std)
    return (X - X.mean(axis=0)) / std


def distances_from_first(X):
    X = np.asarray(X, dtype=float)
    D = X[1:] - X[0]
    return np.sqrt((D ** 2).sum(axis=1))
