from sklearn.model_selection import GroupKFold, StratifiedKFold, TimeSeriesSplit


def choose_cv(kind, n_splits=5):
    if kind == "groups":
        return GroupKFold(n_splits=n_splits)
    if kind == "time":
        return TimeSeriesSplit(n_splits=n_splits)
    if kind == "classes":
        return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=0)
    raise ValueError(f"unknown kind {kind!r}")
