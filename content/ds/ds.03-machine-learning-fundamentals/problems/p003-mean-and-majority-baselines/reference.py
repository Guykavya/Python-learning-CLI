import numpy as np


def baseline_predict(y_train, n, task):
    y = np.asarray(y_train)
    if task == "regression":
        return np.full(n, y.mean())
    if task == "classification":
        values, counts = np.unique(y, return_counts=True)
        return np.full(n, values[np.argmax(counts)])
    raise ValueError(f"task must be 'regression' or 'classification', got {task!r}")
