import numpy as np


def at_k(y, score, k):
    y = np.asarray(y)
    score = np.asarray(score, dtype=float)
    if not 1 <= k <= len(y):
        raise ValueError("k must be between 1 and the number of rows")
    top = np.argsort(-score, kind="stable")[:k]
    precision = float(y[top].mean())
    total = y.sum()
    recall = float(y[top].sum() / total) if total else 0.0
    return precision, recall
