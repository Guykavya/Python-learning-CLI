from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline


def honest_selection_score(X, y, k):
    pipe = Pipeline([("select", SelectKBest(f_classif, k=k)),
                     ("clf", LogisticRegression(max_iter=2000))])
    return float(cross_val_score(pipe, X, y, cv=5, scoring="roc_auc").mean())
