import dataclasses
import hashlib

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def data_fingerprint(df):
    h = hashlib.sha256()
    h.update(",".join(map(str, df.columns)).encode())
    h.update(pd.util.hash_pandas_object(df, index=False).to_numpy().tobytes())
    return h.hexdigest()[:16]


def run_experiment(cfg, df):
    X = df[list(cfg.features)]
    y = df["churned"].to_numpy()
    Xa, Xb, ya, yb = train_test_split(X, y, test_size=cfg.test_size, random_state=cfg.seed, stratify=y)
    model = make_pipeline(StandardScaler(), LogisticRegression(C=cfg.C, max_iter=2000, random_state=cfg.seed)).fit(Xa, ya)
    p = model.predict_proba(Xb)[:, 1]
    return {"config": dataclasses.asdict(cfg),
            "data": {"fingerprint": data_fingerprint(df), "rows": len(df)},
            "metrics": {"test_auc": round(float(roc_auc_score(yb, p)), 6),
                        "test_brier": round(float(brier_score_loss(yb, p)), 6)}}
