# Sample without replacement

Chapter sections 13.3 (sampling) and 9 (fancy indexing). Write `sample_rows(x, k, rng)`: pick `k` **different** rows of the array `x` at random, using the Generator `rng`, and return them as a new array.

- `x` has shape `(n,)` or `(n, m)`; the result has shape `(k,)` or `(k, m)` and the same dtype as `x`.
- No row may be picked twice (positions, not values: if `x` has two equal rows, both may appear once each).
- `k = 0` gives an empty result with the right shape, e.g. `(0, m)`. `k > n` or `k < 0` raise `ValueError` with a message that names `k` and `n`.
- Do **not** shuffle or change `x` (remember: `rng.shuffle` works in place). The result must be a new array: changing it must not change `x`.
- Use only the `rng` you are given. The order of the picked rows is the order in which they were drawn.

## Example

```python
x = np.array([[0, 10], [1, 11], [2, 12], [3, 13], [4, 14]])
s = sample_rows(x, 3, np.random.default_rng(39))
s.shape, s.dtype
# ((3, 2), dtype('int64'))
# s holds 3 different rows of x; with NumPy 2.5.4 they were [[2, 12], [1, 11], [3, 13]] (another version may differ)
```
