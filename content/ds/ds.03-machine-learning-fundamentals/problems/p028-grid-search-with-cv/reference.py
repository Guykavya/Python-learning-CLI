from sklearn.model_selection import GridSearchCV


def tune(model, grid, X, y, scoring=None):
    gs = GridSearchCV(model, grid, cv=5, scoring=scoring).fit(X, y)
    return gs.best_params_, float(gs.best_score_)
