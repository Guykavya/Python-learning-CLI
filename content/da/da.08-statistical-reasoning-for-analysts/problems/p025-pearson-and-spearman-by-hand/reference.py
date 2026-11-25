import numpy as np
from scipy.stats import rankdata


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("need two variables of the same length, at least 2 points")
    dx, dy = x - x.mean(), y - y.mean()
    denom = np.sqrt((dx ** 2).sum() * (dy ** 2).sum())
    if denom == 0:
        raise ValueError("r is undefined when one variable does not vary")
    return float((dx * dy).sum() / denom)


def spearman(x, y):
    return pearson(rankdata(x), rankdata(y))
