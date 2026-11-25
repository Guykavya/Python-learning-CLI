# Overfitting, measured

Chapters 5 and 7. Write `overfit_report(X, y, model, seed=0)` that measures how much a model overfits and whether more data are expected to help.

Use `sklearn.model_selection.learning_curve` with `train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0]`, `cv=KFold(5, shuffle=True, random_state=seed)` and `scoring="neg_root_mean_squared_error"`. Take the fold means of the training and validation RMSE (positive numbers) and compute the gap `validation - train` at each size. Return a dict:

| key | value |
|---|---|
| `"gap"` | the gap at the largest size |
| `"rel_gap"` | that gap divided by the validation RMSE at the largest size |
| `"high_variance"` | `rel_gap > 0.15` (a plain `bool`) |
| `"more_data_helps"` | `high_variance` **and** the gap at the largest size is **smaller** than the gap at the 60% size (the third point): the gap is still shrinking (a plain `bool`) |

## Example

```text
LinearRegression on diabetes:           rel_gap 0.02  high_variance False   more_data_helps False
fully grown DecisionTreeRegressor:       rel_gap 1.00  high_variance True    more_data_helps False   # the gap is not shrinking
degree-2 polynomial, 65 features:        rel_gap 0.17  high_variance True    more_data_helps True    # the gap shrinks with n
```
