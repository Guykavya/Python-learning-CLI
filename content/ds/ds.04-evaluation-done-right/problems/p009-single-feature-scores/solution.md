## Approach

One tiny model per column, the same folds for all. The leaky column stands out because it alone is worth far more than any honest signal.

## Code

```python
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier


def single_feature_auc(X, y, cv=5):
    scores = {}
    for col in X.columns:
        m = DecisionTreeClassifier(max_depth=3, random_state=0)
        scores[col] = float(cross_val_score(m, X[[col]], y, cv=cv, scoring="roc_auc").mean())
    return pd.Series(scores, name="single_feature_auc").sort_values(ascending=False)
```

## Complexity

`p * cv` small tree fits.

## Another way

Mutual information (`mutual_info_classif`) ranks columns without a model; the cross-validated AUC is easier to read.
