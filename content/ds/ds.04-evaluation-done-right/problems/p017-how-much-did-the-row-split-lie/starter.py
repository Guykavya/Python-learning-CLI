from sklearn.model_selection import GroupKFold, KFold, cross_val_score


def row_vs_group_cv(X, y, groups, model):
    """(row-wise 5-fold CV AUC, GroupKFold(5) CV AUC) for the same model."""
    raise NotImplementedError
