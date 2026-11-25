import numpy as np
from sklearn.model_selection import GroupShuffleSplit


def group_split(df, group_col, test_frac, seed):
    """(train positions, test positions), sorted; no group on both sides."""
    raise NotImplementedError
