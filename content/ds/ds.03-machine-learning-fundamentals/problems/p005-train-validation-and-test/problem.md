# Train, validation and test

Chapter section 4. One held-out set is not enough once you use it to choose between models. Keep **three** sets: training (fit), validation (choose) and test (one final honest score).

Write `three_way_split(X, y, val=0.2, test=0.2, seed=0)` returning six arrays in this order:

```text
X_train, X_val, X_test, y_train, y_val, y_test
```

- the rows are **shuffled** with `np.random.default_rng(seed).permutation(n)` before cutting
- the test set takes `round(n * test)` rows, the validation set `round(n * val)` rows, the training set the rest
- `X` and `y` are NumPy arrays; row `i` of `X` always stays with row `i` of `y`
- the same seed gives the same split, a different seed a different one
- `val + test` must be below 1, otherwise `ValueError`

## Example

```text
n = 100, val = 0.2, test = 0.2     ->  60 / 20 / 20 rows
```
