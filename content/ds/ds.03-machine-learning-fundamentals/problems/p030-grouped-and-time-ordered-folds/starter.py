from sklearn.model_selection import GroupKFold, StratifiedKFold, TimeSeriesSplit


def choose_cv(kind, n_splits=5):
    """The right splitter for 'groups', 'time' or 'classes'."""
    raise NotImplementedError
