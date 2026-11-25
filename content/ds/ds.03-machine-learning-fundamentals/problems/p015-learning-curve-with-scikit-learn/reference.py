import pandas as pd
from sklearn import model_selection


def real_curve(est, X, y, scoring="neg_root_mean_squared_error"):
    sizes, tr, va = model_selection.learning_curve(
        est, X, y, train_sizes=[0.1, 0.2, 0.4, 0.7, 1.0],
        cv=model_selection.KFold(5, shuffle=True, random_state=0), scoring=scoring)
    is_error = scoring.startswith("neg_")
    sign = -1 if is_error else 1
    train = sign * tr.mean(axis=1)
    validation = sign * va.mean(axis=1)
    gap = (validation - train) if is_error else (train - validation)
    return pd.DataFrame({"n_train": sizes, "train": train, "validation": validation, "gap": gap})
