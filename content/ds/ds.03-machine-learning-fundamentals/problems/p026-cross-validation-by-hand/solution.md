## Approach

Loop over the folds, train on the complement, score on the fold, and collect the scores. A fresh model every time guarantees no information passes from one fold to another.

## Code

```python
import numpy as np


def cross_val_manual(make_model, X, y, folds, scorer):
    X = np.asarray(X)
    y = np.asarray(y)
    scores = []
    for val in folds:
        val = np.asarray(val)
        mask = np.ones(len(y), dtype=bool)
        mask[val] = False
        model = make_model().fit(X[mask], y[mask])
        scores.append(scorer(y[val], model.predict(X[val])))
    return np.array(scores)
```

## Complexity

`k` fits.

## Another way

`cross_val_score(model, X, y, cv=[(train, val), ...])` accepts a list of `(train_idx, val_idx)` pairs.
