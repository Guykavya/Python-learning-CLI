# Pick pairs

Chapter sections 9.1, 9.2 and 9.4. Two index arrays used together pick **pairs**: `m[[0, 2], [1, 3]]` is
`[m[0, 1], m[2, 3]]`, not a 2 × 2 block. Write:

- `pick(matrix, rows, cols)`: the values `matrix[rows[i], cols[i]]` for every `i`. `rows` and `cols` are lists or
  integer arrays of the same shape (or shapes that broadcast); the result has that shape. Negative indexes count
  from the end, as usual.
- `diagonal_of_top(matrix, k)`: the first `k` values of the main diagonal, `[matrix[0, 0], matrix[1, 1], ...,
  matrix[k-1, k-1]]`, as a 1-D array. `k = 0` gives an empty array.

An index that is out of range must raise `IndexError` (let NumPy's error pass through; do not catch it). For
`diagonal_of_top` that includes a `k` larger than the number of rows or columns. Both results are new arrays (copies):
writing into them does not change `matrix`. No Python loops.

## Example

```python
m = np.arange(20).reshape(4, 5)
pick(m, [0, 2, 3], [1, 3, 0]).tolist()   # [1, 13, 15]
diagonal_of_top(m, 3).tolist()           # [0, 6, 12]
diagonal_of_top(m, 5)                    # IndexError (only 4 rows)
```
