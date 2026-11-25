## Approach

Each training row is encoded by a model (the category means) that was fitted without it, exactly like a cross-validated prediction. The test rows use the means of the whole training set, which is what the deployed model would use.

## Code

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold


def target_encode(train_col, train_y, test_col, n_folds=5, seed=0):
    col = np.asarray(train_col)
    y = np.asarray(train_y, dtype=float)
    train_enc = np.empty(len(col))
    for fit_idx, enc_idx in KFold(n_folds, shuffle=True, random_state=seed).split(col):
        means = pd.Series(y[fit_idx]).groupby(col[fit_idx]).mean().to_dict()
        fallback = float(y[fit_idx].mean())
        train_enc[enc_idx] = [means.get(c, fallback) for c in col[enc_idx]]
    full = pd.Series(y).groupby(col).mean().to_dict()
    overall = float(y.mean())
    test_enc = np.array([full.get(c, overall) for c in np.asarray(test_col)], dtype=float)
    return train_enc, test_enc
```

## Complexity

O(n_folds * n).

## Another way

`sklearn.preprocessing.TargetEncoder` does out-of-fold encoding inside `fit_transform` and adds smoothing towards the overall mean for rare categories.
