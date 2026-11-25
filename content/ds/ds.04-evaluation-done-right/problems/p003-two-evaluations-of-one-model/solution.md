## Approach

Same folds, same model, one column different: the difference in AUC is the value of that column, and an enormous value is the first sign of a target leak.

## Code

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score


def two_evaluations(X, y, model, suspect):
    if suspect not in X.columns:
        raise KeyError(suspect)
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    with_ = cross_val_score(model, X, y, cv=cv, scoring="roc_auc").mean()
    without = cross_val_score(model, X.drop(columns=[suspect]), y, cv=cv, scoring="roc_auc").mean()
    return float(with_), float(without)
```

## Complexity

Ten model fits.

## Another way

Permutation importance on a hold-out set shows the same thing for every column at once.
