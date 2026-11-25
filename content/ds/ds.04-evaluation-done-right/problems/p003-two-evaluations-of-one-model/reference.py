from sklearn.model_selection import StratifiedKFold, cross_val_score


def two_evaluations(X, y, model, suspect):
    if suspect not in X.columns:
        raise KeyError(suspect)
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    with_ = cross_val_score(model, X, y, cv=cv, scoring="roc_auc").mean()
    without = cross_val_score(model, X.drop(columns=[suspect]), y, cv=cv, scoring="roc_auc").mean()
    return float(with_), float(without)
