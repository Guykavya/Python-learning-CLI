import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier


def single_feature_auc(X, y, cv=5):
    scores = {}
    for col in X.columns:
        m = DecisionTreeClassifier(max_depth=3, random_state=0)
        scores[col] = float(cross_val_score(m, X[[col]], y, cv=cv, scoring="roc_auc").mean())
    return pd.Series(scores, name="single_feature_auc").sort_values(ascending=False)
