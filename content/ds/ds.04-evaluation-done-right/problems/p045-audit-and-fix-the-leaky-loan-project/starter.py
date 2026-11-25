import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler, TargetEncoder
from sklearn.tree import DecisionTreeClassifier

FEATS_PLAIN = ["income", "debt_ratio", "loan_amount", "credit_score", "employment_years", "birth_year"]


def audit(df):
    """{'leaky_column', 'duplicate_rows', 'group_column', 'leaky_auc', 'honest_auc'}."""
    raise NotImplementedError
