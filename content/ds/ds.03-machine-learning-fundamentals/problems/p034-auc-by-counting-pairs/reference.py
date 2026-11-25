import numpy as np
from scipy.stats import rankdata


def auc_by_pairs(y, score):
    y = np.asarray(y)
    score = np.asarray(score, dtype=float)
    n_pos = int(np.sum(y == 1))
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("AUC needs both classes")
    ranks = rankdata(score)
    return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))
