from sklearn.model_selection import StratifiedKFold, cross_val_score


def two_evaluations(X, y, model, suspect):
    """(cv AUC with all columns, cv AUC without `suspect`) on the same 5 shuffled stratified folds."""
    raise NotImplementedError
