import pandas as pd
from sklearn import model_selection


def real_curve(est, X, y, scoring="neg_root_mean_squared_error"):
    """DataFrame n_train, train, validation, gap from sklearn's learning_curve (errors made positive)."""
    raise NotImplementedError
