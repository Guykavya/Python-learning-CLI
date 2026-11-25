import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def churn_auc(df, seed=0, scaler_cls=StandardScaler):
    X = pd.get_dummies(df.drop(columns="churned"), dtype=float)
    y = df["churned"].to_numpy()
    Xs = scaler_cls().fit_transform(X)
    Xs = SelectKBest(f_classif, k=8).fit_transform(Xs, y)
    Xa, Xb, ya, yb = train_test_split(Xs, y, test_size=0.3, random_state=seed, stratify=y)
    model = LogisticRegression(max_iter=2000).fit(Xa, ya)
    return float(roc_auc_score(yb, model.predict_proba(Xb)[:, 1]))
