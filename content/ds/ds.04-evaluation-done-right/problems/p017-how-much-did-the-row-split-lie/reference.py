from sklearn.model_selection import GroupKFold, KFold, cross_val_score


def row_vs_group_cv(X, y, groups, model):
    row = cross_val_score(model, X, y, cv=KFold(5, shuffle=True, random_state=0), scoring="roc_auc").mean()
    grp = cross_val_score(model, X, y, cv=GroupKFold(5), groups=groups, scoring="roc_auc").mean()
    return float(row), float(grp)
