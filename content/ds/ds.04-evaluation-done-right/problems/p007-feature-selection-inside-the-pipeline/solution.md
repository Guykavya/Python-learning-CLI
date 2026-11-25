## Approach

Inside a pipeline, `cross_val_score` refits every step on each training fold, so the selector never sees the validation fold's labels.

## Code

```python
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline


def honest_selection_score(X, y, k):
    pipe = Pipeline([("select", SelectKBest(f_classif, k=k)),
                     ("clf", LogisticRegression(max_iter=2000))])
    return float(cross_val_score(pipe, X, y, cv=5, scoring="roc_auc").mean())
```

## Complexity

5 selections (O(n p)) and 5 small fits.

## Another way

Write the folds by hand and call `SelectKBest(...).fit(X_train_fold, y_train_fold)` inside the loop. The pipeline does exactly that for you.
