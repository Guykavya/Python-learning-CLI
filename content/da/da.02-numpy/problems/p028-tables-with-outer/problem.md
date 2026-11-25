# Tables with `outer`

Chapter sections 10.7 (ufunc methods) and 11.6 (outer operations). Every binary ufunc has an `.outer` method that applies the operation to **every pair** of elements: `np.multiply.outer(a, b)[i, j] == a[i] * b[j]`. Write two functions with it (or with the equivalent broadcasting `a[:, None] * b[None, :]`), no Python loops.

## `times_table(n)`

The `n × n` multiplication table of `1 … n`: entry `[i, j]` is `(i + 1) * (j + 1)`. Integer dtype. `times_table(0)` is an empty array of shape `(0, 0)`.

## `pairwise_diff(a, b)`

For 1-D `a` (length `n`) and `b` (length `m`), the table of shape `(n, m)` whose entry `[i, j]` is `a[i] - b[j]`. Lists are allowed. Integer input gives an integer table, float input a float table. If `b` is empty the shape is `(n, 0)`.

## Example

```python
times_table(3)
# array([[1, 2, 3],
#        [2, 4, 6],
#        [3, 6, 9]])
pairwise_diff([3, 7, 1, 9], [2, 8, 5])
# array([[ 1, -5, -2],
#        [ 5, -1,  2],
#        [-1, -7, -4],
#        [ 7,  1,  4]])
```
