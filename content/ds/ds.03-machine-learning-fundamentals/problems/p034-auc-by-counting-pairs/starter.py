import numpy as np
from scipy.stats import rankdata


def auc_by_pairs(y, score):
    """AUC in O(n log n) from average ranks; ValueError if only one class is present."""
    raise NotImplementedError
