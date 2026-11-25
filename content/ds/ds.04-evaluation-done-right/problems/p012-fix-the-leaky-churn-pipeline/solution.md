## The bugs and the fix

- Scaling and selection were fitted on all 4,000 rows, including the 1,200 that are later used for testing. Moving them into a pipeline fitted on the training rows removes both leaks.
- `retention_offer_sent` is a consequence of the outcome: it is removed from the features.

## Fixed code

```python
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def churn_auc(df, seed=0, scaler_cls=StandardScaler):
    drop = [c for c in ("churned", "retention_offer_sent") if c in df.columns]
    X = pd.get_dummies(df.drop(columns=drop), dtype=float)
    y = df["churned"].to_numpy()
    Xa, Xb, ya, yb = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    pipe = make_pipeline(scaler_cls(), SelectKBest(f_classif, k=8), LogisticRegression(max_iter=2000))
    pipe.fit(Xa, ya)
    return float(roc_auc_score(yb, pipe.predict_proba(Xb)[:, 1]))
```

## Another way

Wrap the pipeline in `cross_val_score` on the training part to compare models, and keep the test part for one final number.
