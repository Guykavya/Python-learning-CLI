# How many components keep 95%?

Chapter section 5.3. How many principal components do you need to keep a given share of the total variance? Add up the sorted variance shares until you reach the target.

Write `components_for(X, share)` returning the smallest `k` such that the first `k` components explain at least `share` of the total variance (use the SVD of the centred data; the variance of component `i` is proportional to `s[i]**2`). A `share` of 1.0 returns the number of components with non-zero variance.

## Example

```text
Data built from 3 strong directions plus a little noise in 6 columns:
components_for(X, 0.95) -> 3
```
