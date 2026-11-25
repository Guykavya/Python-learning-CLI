## Hint 1

For a training row in fold `f`, which rows are allowed to contribute to its category mean? Which object gives you the two sets of row positions for each fold?

## Hint 2

```text
for fit_idx, enc_idx in KFold(n_folds, shuffle=True, random_state=seed).split(train_col):
    means = mean of y[fit_idx] grouped by col[fit_idx]; fallback = mean(y[fit_idx])
    train_enc[enc_idx] = [means.get(c, fallback) for c in col[enc_idx]]
test_enc = [full_means.get(c, mean(y)) for c in test_col]
```
