import numpy as np
import statsmodels.formula.api as smf


def holdout_rmse(df, formula, test_frac=0.25, seed=0):
    """{'train_rmse', 'test_rmse'} after fitting on a random (1 - test_frac) of the rows."""
    raise NotImplementedError
