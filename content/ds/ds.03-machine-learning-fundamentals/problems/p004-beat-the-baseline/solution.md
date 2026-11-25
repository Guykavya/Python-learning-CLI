## Approach

Score the model and the do-nothing baseline on the same held-out rows with the same metric, and compare strictly: a tie is not a win.

## Code

```python
import numpy as np


def beats_baseline(model, X_tr, y_tr, X_te, y_te, task):
    y_tr = np.asarray(y_tr)
    y_te = np.asarray(y_te)
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    if task == "regression":
        m = float(np.sqrt(np.mean((y_te - pred) ** 2)))
        b = float(np.sqrt(np.mean((y_te - y_tr.mean()) ** 2)))
        return m, b, bool(m < b)
    if task == "classification":
        values, counts = np.unique(y_tr, return_counts=True)
        majority = values[np.argmax(counts)]
        m = float(np.mean(pred == y_te))
        b = float(np.mean(majority == y_te))
        return m, b, bool(m > b)
    raise ValueError(f"unknown task {task!r}")
```

## Complexity

One fit plus O(n) scoring.

## Another way

`DummyRegressor` / `DummyClassifier` and `model.score(...)` give the baseline and the model score with less code, but make sure both are measured on the **test** rows.
