# Target encoding without leaking

Chapter section 3. **Target encoding** replaces a category (a postcode, a shop) by the average target of its rows. Computed on all rows, a row's encoding contains **its own label**, which is a leak (very strong for rare categories). The fix for the training rows is **out-of-fold** encoding.

Write `target_encode(train_col, train_y, test_col, n_folds=5, seed=0)` returning `(train_enc, test_enc)`, two float NumPy arrays:

- **training rows**: split the training rows with `KFold(n_folds, shuffle=True, random_state=seed)`; for the rows of each fold, use the per-category mean of `train_y` computed on the **other** folds. If a category does not appear in the other folds, use the mean of `train_y` over the other folds.
- **test rows**: the per-category mean of `train_y` over **all** training rows; a category never seen in training gets the overall training mean.

`train_col`, `test_col` are 1-D arrays (or Series) of category labels; `train_y` is 0/1.

## Example

```text
a row's encoding never depends on its own label: change train_y[i] and train_enc[i] stays the same
test_enc for "north" = mean of train_y over all training rows with "north"
```
