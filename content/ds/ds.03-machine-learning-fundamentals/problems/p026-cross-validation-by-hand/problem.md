# Cross-validation by hand

Chapter section 9. In k-fold cross-validation every fold is the validation set once; the model is trained on the other `k - 1` folds and scored on the held-out one.

Write `cross_val_manual(make_model, X, y, folds, scorer)`:

- `folds` is a list of **validation index arrays** (as returned by the previous problem); they partition the rows
- for each fold: train indices are all the other rows; build a **fresh** model with `make_model()`, fit it on the training rows, predict the validation rows, and compute `scorer(y_val, predictions)`
- return a NumPy array with one score per fold, in the order of `folds`
- `X` and `y` are NumPy arrays

## Example

```text
folds = [[0, 1], [2, 3], [4, 5]]; scorer = r2_score
cross_val_manual(LinearRegression, X, y, folds, r2_score)  ->  array([0.91, 0.88, 0.93])
```
