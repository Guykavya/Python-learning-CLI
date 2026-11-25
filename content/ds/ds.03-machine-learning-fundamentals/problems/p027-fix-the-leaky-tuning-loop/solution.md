## The bug

The loop evaluates every alpha on `X_test, y_test` and keeps the best test score, then reports it. The test set was used to **choose**, so the reported score is the best of 13 noisy numbers, an optimistic estimate (see problem 8).

## Fixed code

```python
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score


def tune_and_report(X_train, y_train, X_test, y_test, alphas):
    best_alpha, best_cv = None, -np.inf
    for a in alphas:
        cv = float(np.mean(cross_val_score(Ridge(alpha=a), X_train, y_train, cv=5)))
        if cv > best_cv:
            best_alpha, best_cv = a, cv
    model = Ridge(alpha=best_alpha).fit(X_train, y_train)
    return best_alpha, float(model.score(X_test, y_test))
```

## Another way

`GridSearchCV(Ridge(), {"alpha": alphas}, cv=5).fit(X_train, y_train)` does the search and the refit; then call `.score(X_test, y_test)` once.
