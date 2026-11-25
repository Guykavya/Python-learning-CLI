# K-fold indices by hand

Chapter section 9. **K-fold cross-validation** cuts the rows into `k` folds; each fold is the validation set once.

Write `kfold_indices(n, k, seed=0)` returning a **list of `k` NumPy arrays**: the validation indices of each fold.

- shuffle first: `idx = np.random.default_rng(seed).permutation(n)`, then cut it with `np.array_split(idx, k)`
- the folds are disjoint, together cover `0 .. n-1`, and their sizes differ by at most 1
- `k < 2` or `k > n`: `ValueError`
- same seed, same folds; different seed, different folds

## Example

```text
kfold_indices(10, 5, seed=0)   ->  five arrays of 2 indices each
kfold_indices(11, 5, seed=0)   ->  sizes [3, 2, 2, 2, 2]
```
