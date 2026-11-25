import numpy as np
import pandas as pd
from sklearn.model_selection import KFold


def target_encode(train_col, train_y, test_col, n_folds=5, seed=0):
    """(out-of-fold encodings for train, full-train category means for test)."""
    raise NotImplementedError
