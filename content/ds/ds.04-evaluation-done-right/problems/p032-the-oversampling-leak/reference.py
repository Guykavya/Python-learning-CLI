import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold


def oversample(X, y, factor):
    X = np.asarray(X); y = np.asarray(y)
    pos = np.where(y == 1)[0]
    extra = np.tile(pos, factor - 1)
    return np.vstack([X, X[extra]]), np.concatenate([y, y[extra]])


def _cv(make_model, X, y, seed, prep):
    scores = []
    for tr, va in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y):
        Xa, ya = prep(X[tr], y[tr])
        model = make_model().fit(Xa, ya)
        scores.append(roc_auc_score(y[va], model.predict_proba(X[va])[:, 1]))
    return float(np.mean(scores))


def cv_oversample_first(make_model, X, y, factor, seed=0):
    Xo, yo = oversample(X, y, factor)
    return _cv(make_model, Xo, yo, seed, lambda a, b: (a, b))


def cv_oversample_inside(make_model, X, y, factor, seed=0):
    X = np.asarray(X); y = np.asarray(y)
    return _cv(make_model, X, y, seed, lambda a, b: oversample(a, b, factor))
