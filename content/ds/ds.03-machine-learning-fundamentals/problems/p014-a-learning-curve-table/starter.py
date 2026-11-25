import numpy as np
import pandas as pd


def learning_curve_table(make_model, X, y, sizes, val_X, val_y, repeats=30, seed=0):
    """DataFrame n_train, train_rmse, val_rmse, gap (means over `repeats` random training subsets)."""
    raise NotImplementedError
