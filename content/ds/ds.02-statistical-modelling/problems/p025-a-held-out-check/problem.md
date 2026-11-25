# A held-out check

Chapter section 11. Fit on one part of the data, measure the error on the part the model never saw.

Write `holdout_rmse(df, formula, test_frac=0.25, seed=0)`:

1. Make a random split exactly like this: `idx = np.random.default_rng(seed).permutation(len(df))`, `cut = int(len(df) * (1 - test_frac))`, train rows `idx[:cut]`, test rows `idx[cut:]` (positions, use `df.iloc`).
2. Fit `smf.ols(formula, data=train)`.
3. Return a dict `{"train_rmse": ..., "test_rmse": ...}`: the root mean squared error of the model's predictions against the response of the same rows, for the training rows and for the test rows. The response is the left side of the formula and is a plain column called `y` in the test data.

## Example

```text
df: 60 rows, a response y that depends on x0 only, and 20 junk columns j0..j19
holdout_rmse(df, "y ~ x0 + j0 + ... + j19")  -> {"train_rmse": 1.4, "test_rmse": 2.2}   # the gap = overfitting
holdout_rmse(df, "y ~ x0")                   -> {"train_rmse": 2.0, "test_rmse": 2.0}   # no gap
```
