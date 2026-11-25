from sklearn.model_selection import GridSearchCV


def tune(model, grid, X, y, scoring=None):
    """(best_params, best_cv_score) from a 5-fold grid search."""
    raise NotImplementedError
