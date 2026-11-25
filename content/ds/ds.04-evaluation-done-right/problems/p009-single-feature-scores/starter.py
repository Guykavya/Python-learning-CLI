import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier


def single_feature_auc(X, y, cv=5):
    """Series of cross-validated AUC of a depth-3 tree on each column alone, highest first."""
    raise NotImplementedError
