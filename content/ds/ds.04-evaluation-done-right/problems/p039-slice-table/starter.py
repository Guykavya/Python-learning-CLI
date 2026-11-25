import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


def slice_table(frame, y, p, col):
    """Per value of col: rows, base_rate, mean_p, auc (NaN for one-class slices)."""
    raise NotImplementedError
