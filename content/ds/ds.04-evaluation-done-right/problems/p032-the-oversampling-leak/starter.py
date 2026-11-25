import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold


def oversample(X, y, factor):
    """Every positive row `factor` times in total (originals first, then the copies)."""
    raise NotImplementedError


def cv_oversample_first(make_model, X, y, factor, seed=0):
    """Oversample everything, then 5-fold CV AUC (the leak)."""
    raise NotImplementedError


def cv_oversample_inside(make_model, X, y, factor, seed=0):
    """5-fold CV AUC with oversampling of each training fold only."""
    raise NotImplementedError
