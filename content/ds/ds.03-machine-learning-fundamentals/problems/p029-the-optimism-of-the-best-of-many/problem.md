# The optimism of the best of many

Chapter section 10. If you try many models on one validation set and keep the best, its score is flattering even when **no model has any skill**. You will measure how flattering.

Write `best_of_many_optimism(n_models, seed)`. Use **one** `rng = np.random.default_rng(seed)` and draw, **in this order**:

1. `X_val = rng.normal(size=(100, 10))`, then `y_val = rng.integers(0, 2, 100)`
2. `X_test = rng.normal(size=(1000, 10))`, then `y_test = rng.integers(0, 2, 1000)`
3. for each of the `n_models` candidate "models": `w = rng.normal(size=10)`; the model predicts class 1 when `X @ w > 0`. Its validation accuracy is the share of correct predictions on `X_val`

Keep the candidate with the **highest** validation accuracy (the first one on a tie). Return `(best_val_accuracy, test_accuracy_of_that_candidate)`. The labels are pure coin flips, so **no candidate has any real skill**: every true accuracy is 50%.

## Example

```text
best_of_many_optimism(1, 0)     ->  (0.53, 0.51)     # one model: no selection, no optimism
best_of_many_optimism(300, 0)   ->  (0.64, 0.51)     # the best of 300 looks good on validation, is a coin on test
```
