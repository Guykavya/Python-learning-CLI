## Approach

For every training size, draw several random training subsets, fit, and average the two errors. The average removes the luck of a single subset.

## Code

```python
import numpy as np
import pandas as pd


def _rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def learning_curve_table(make_model, X, y, sizes, val_X, val_y, repeats=30, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for n in sizes:
        tr, va = [], []
        for _ in range(repeats):
            idx = rng.choice(len(X), n, replace=False)
            m = make_model().fit(X[idx], y[idx])
            tr.append(_rmse(y[idx], m.predict(X[idx])))
            va.append(_rmse(val_y, m.predict(val_X)))
        rows.append((n, float(np.mean(tr)), float(np.mean(va))))
    out = pd.DataFrame(rows, columns=["n_train", "train_rmse", "val_rmse"])
    out["gap"] = out["val_rmse"] - out["train_rmse"]
    return out
```

## Complexity

`len(sizes) * repeats` fits.

## Another way

`sklearn.model_selection.learning_curve` does this with cross-validation inside (next problem).
