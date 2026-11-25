import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler, TargetEncoder
from sklearn.tree import DecisionTreeClassifier

FEATS_PLAIN = ["income", "debt_ratio", "loan_amount", "credit_score", "employment_years", "birth_year"]


def _leaky_column(df):
    y = df["default"]
    best, best_auc = None, 0.0
    for col in df.columns:
        if col in ("loan_id", "customer_id", "default"):
            continue
        auc = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), df[[col]], y, cv=5, scoring="roc_auc").mean()
        if auc > best_auc:
            best, best_auc = col, auc
    return best if best_auc > 0.9 else None


def audit(df):
    leak = _leaky_column(df)
    dups = int(df.duplicated("loan_id").sum())
    u = df.drop_duplicates("loan_id").reset_index(drop=True)
    group = next((c for c in df.columns if c.endswith("_id") and c != "loan_id" and u[c].nunique() < len(u)), None)

    y = df["default"].to_numpy()
    feats = FEATS_PLAIN + ([leak] if leak else [])
    tr, te = train_test_split(np.arange(len(df)), test_size=0.25, random_state=0)
    lp = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(df[feats].iloc[tr], y[tr])
    leaky_auc = roc_auc_score(y[te], lp.predict_proba(df[feats].iloc[te])[:, 1])

    yu = u["default"].to_numpy()
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=0).split(u, yu, u[group]))
    pre = ColumnTransformer([("pc", TargetEncoder(random_state=0), ["postcode"])], remainder="passthrough")
    pipe = Pipeline([("pre", pre), ("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=3000))])
    X = u[FEATS_PLAIN + ["postcode"]]
    pipe.fit(X.iloc[tr], yu[tr])
    honest_auc = roc_auc_score(yu[te], pipe.predict_proba(X.iloc[te])[:, 1])

    return {"leaky_column": leak, "duplicate_rows": dups, "group_column": group,
            "leaky_auc": float(leaky_auc), "honest_auc": float(honest_auc)}
