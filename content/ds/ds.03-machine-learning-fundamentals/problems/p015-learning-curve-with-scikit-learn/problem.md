# Learning curve with scikit-learn

Chapter section 7.2. `sklearn.model_selection.learning_curve` computes the same table with cross-validation inside. Its output is awkward: arrays of scores, and for error scorers (`neg_...`) **negative numbers** (scikit-learn always maximises a score).

Write `real_curve(est, X, y, scoring="neg_root_mean_squared_error")` that calls `learning_curve` with `train_sizes=[0.1, 0.2, 0.4, 0.7, 1.0]` and `cv=KFold(5, shuffle=True, random_state=0)` and returns a DataFrame with the columns `n_train, train, validation, gap` (in that order):

- `n_train`: the training sizes returned by `learning_curve`
- `train`, `validation`: the **mean over the folds** of the training and validation scores; if `scoring` starts with `neg_`, flip the sign so they are positive errors
- `gap`: for an error scorer (`neg_...`) `validation - train` (how much worse on new data); for any other scorer (accuracy, R2) `train - validation`

## Example

```text
real_curve(LinearRegression(), X, y)   # diabetes data
 n_train   train  validation    gap
      35   39.83       69.78  29.95
     ...
```
