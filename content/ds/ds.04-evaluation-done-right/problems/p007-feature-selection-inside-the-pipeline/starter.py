from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline


def honest_selection_score(X, y, k):
    """Mean 5-fold CV ROC-AUC with SelectKBest INSIDE the pipeline."""
    raise NotImplementedError
