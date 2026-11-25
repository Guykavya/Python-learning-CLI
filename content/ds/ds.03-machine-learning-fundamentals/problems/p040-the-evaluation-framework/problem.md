# The evaluation framework

Chapter section 14 (the module project). Build `Evaluation`, a small class that makes an **honest** model evaluation hard to get wrong. Put `TestSetAlreadyOpened` and `Evaluation` in `solution.py`. NumPy, pandas and scikit-learn are allowed. The chapter's section 14.2 contains a full version for you to compare with; try to write yours from this specification first.

```python
class TestSetAlreadyOpened(RuntimeError): ...

class Evaluation:
    def __init__(self, X, y, task="regression", test_size=0.2, seed=0): ...
```

**Constructor.** `task` is `"regression"` or `"classification"` (anything else: `ValueError`). Split once with `sklearn.model_selection.train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y if classification else None)`. Keep the development part as `self.X_dev, self.y_dev`; keep the sealed test part in the **private** attributes `self._X_test, self._y_test`. Build `self.cv`: `StratifiedKFold(5, shuffle=True, random_state=seed)` for classification, `KFold(5, shuffle=True, random_state=seed)` for regression. `self.scoring` is `"accuracy"` for classification and `"neg_root_mean_squared_error"` for regression.

**Methods.**

| method | what it does |
|---|---|
| `compare(models)` | `models` is a dict `name -> unfitted model`. Cross-validate each on the development data with `self.cv` and `self.scoring`. Return a DataFrame with the columns `model, cv_mean, cv_sd` (`cv_sd` with `ddof=1`). For regression the scores are RMSE (flip the sign: lower is better) and the rows are sorted **ascending**; for classification they are accuracies, sorted **descending**. The index is `0, 1, 2, ...` |
| `baseline()` | `compare` of a single model called `"baseline"` (`DummyRegressor()` or `DummyClassifier(strategy="most_frequent")`); return its first row (a Series) |
| `learning_curve(model, sizes=(0.1, 0.25, 0.5, 0.75, 1.0))` | `sklearn.model_selection.learning_curve` on the development data with `self.cv` and `self.scoring`; DataFrame with the columns `n_train, train, validation, gap` (means over folds; errors made positive for regression). `gap = validation - train` for regression, `train - validation` for classification |
| `diagnose(lc, task="regression")` (a `@staticmethod`) | last row of `lc`; `error = validation` for regression, `1 - validation` for classification; `rel_gap = gap / max(abs(error), 1e-12)`; if `rel_gap > 0.15` return a string that **starts with** `"high variance"`, otherwise a string that **starts with** `"high bias or near the noise floor"` |
| `tune(model, grid)` | `GridSearchCV(model, grid, cv=self.cv, scoring=self.scoring)` fitted on the development data; return `(best_estimator, best_params, abs(best_score))` |
| `final_test(model)` | the **only** method that touches the test set. If it was already called, raise `TestSetAlreadyOpened`. Otherwise fit `model` on the **development** data and predict the test set. Regression: `{"RMSE", "MAE", "R2"}`. Classification: `{"accuracy", "precision", "recall", "F1"}` (macro averages for the last three). Plain floats |

## Example

```text
ev = Evaluation(X, y, task="regression")
ev.compare({"ridge": ridge, "tree": tree})      # table, best first
best, params, cv_rmse = ev.tune(ridge, {"ridge__alpha": [0.1, 1, 10]})
ev.final_test(best)       # {"RMSE": 58.6, "MAE": 46.1, "R2": 0.33}
ev.final_test(best)       # raises TestSetAlreadyOpened
```
