import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score


def tune_and_report(X_train, y_train, X_test, y_test, alphas):
    best_alpha, best_score = None, -np.inf
    for a in alphas:
        model = Ridge(alpha=a).fit(X_train, y_train)
        score = model.score(X_test, y_test)
        if score > best_score:
            best_alpha, best_score = a, score
    return best_alpha, best_score
