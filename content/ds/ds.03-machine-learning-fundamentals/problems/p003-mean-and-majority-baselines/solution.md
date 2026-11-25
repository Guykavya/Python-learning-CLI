## Approach

`np.unique` returns the classes sorted ascending, and `argmax` returns the **first** maximum, which is the smaller class on a tie.

## Code

```python
import numpy as np


def baseline_predict(y_train, n, task):
    y = np.asarray(y_train)
    if task == "regression":
        return np.full(n, y.mean())
    if task == "classification":
        values, counts = np.unique(y, return_counts=True)
        return np.full(n, values[np.argmax(counts)])
    raise ValueError(f"task must be 'regression' or 'classification', got {task!r}")
```

## Complexity

O(m log m) for `unique` on `m` training labels.

## Another way

`sklearn.dummy.DummyRegressor` and `DummyClassifier(strategy="most_frequent")` do this; use them as a referee.
