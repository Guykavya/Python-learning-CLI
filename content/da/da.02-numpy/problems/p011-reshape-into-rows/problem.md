# Reshape into rows

Chapter sections 5.1 and 6.1. A logger writes readings in one long 1-D array, `k` readings per minute. Write
`to_rows(x, k)` that returns the same numbers as a 2-D array with `k` columns (one row per minute):

- use `reshape` with `-1`, so NumPy works out the number of rows;
- the result must be a **view** of `x` (no copy): `np.shares_memory(result, x)` is `True`;
- if `len(x)` is not a multiple of `k`, raise `ValueError` with a message that names **both numbers**,
  for example `"cannot split 10 values into rows of 4"`;
- if `k < 1`, raise `ValueError`.

An empty `x` gives shape `(0, k)`.

## Example

```python
x = np.arange(6)
to_rows(x, 3).tolist()   # [[0, 1, 2], [3, 4, 5]]
to_rows(x, 2).shape      # (3, 2)
to_rows(np.arange(10), 4)
# ValueError: cannot split 10 values into rows of 4
```
