# Grid search with CV

Chapter section 10. A **grid search** tries every combination of the hyperparameters in a grid, scores each with cross-validation on the training data, and keeps the best.

Write `tune(model, grid, X, y, scoring=None)` that runs `GridSearchCV(model, grid, cv=5, scoring=scoring)` on `(X, y)` and returns the tuple `(best_params, best_score)`: the dictionary of the best parameters and the mean cross-validated score of that setting (as `GridSearchCV` reports it, a number where larger is better; for `neg_...` scorers it is negative).

## Example

```text
model = make_pipeline(StandardScaler(), Ridge());  grid = {"ridge__alpha": np.logspace(-3, 3, 13)}
tune(model, grid, X, y, "neg_root_mean_squared_error")  ->  ({"ridge__alpha": 0.1}, -54.69)
```
