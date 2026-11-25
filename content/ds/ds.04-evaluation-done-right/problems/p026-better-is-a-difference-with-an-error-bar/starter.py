import numpy as np
from sklearn.metrics import roc_auc_score


def paired_difference(y, p_model, p_base, reps=500, seed=0):
    """(mean AUC difference, 2.5th percentile, 97.5th percentile) by a paired bootstrap of the rows."""
    raise NotImplementedError
