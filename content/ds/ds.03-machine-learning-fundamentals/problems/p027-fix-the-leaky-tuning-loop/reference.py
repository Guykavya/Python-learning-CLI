import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score


def tune_and_report(X_train, y_train, X_test, y_test, alphas):
    best_alpha, best_cv = None, -np.inf
    for a in alphas:
        cv = float(np.mean(cross_val_score(Ridge(alpha=a), X_train, y_train, cv=5)))
        if cv > best_cv:
            best_alpha, best_cv = a, cv
    model = Ridge(alpha=best_alpha).fit(X_train, y_train)
    return best_alpha, float(model.score(X_test, y_test))
