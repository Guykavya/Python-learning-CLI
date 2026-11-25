import numpy as np


def cross_val_manual(make_model, X, y, folds, scorer):
    """Array of scorer(y_val, pred) per fold; each fold is held out once, with a fresh model."""
    raise NotImplementedError
