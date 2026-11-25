# Mean and majority baselines

Chapter section 3. Before building a model, ask what a model that **ignores the features** would score. For regression it predicts the mean of the training targets, for classification the most frequent training class. Any real model has to beat that.

Write `baseline_predict(y_train, n, task)` returning a NumPy array of `n` identical predictions:

- `task == "regression"`: the mean of `y_train`
- `task == "classification"`: the most frequent value of `y_train`; if two classes tie, the **smaller** value
- any other `task`: `ValueError`

## Example

```text
baseline_predict([1, 2, 3, 6], 3, "regression")        ->  array([3., 3., 3.])
baseline_predict([0, 1, 1, 2], 2, "classification")    ->  array([1, 1])
baseline_predict([0, 0, 1, 1], 2, "classification")    ->  array([0, 0])     # tie: the smaller class
```
