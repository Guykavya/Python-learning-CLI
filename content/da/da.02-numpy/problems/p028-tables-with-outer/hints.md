## Hint 1

What does `np.multiply.outer([1, 2, 3], [1, 2, 3])` print? Which array of numbers do you need to feed it for the table of `1 … n`?

## Hint 2

```text
times_table:   k = arange(1, n + 1);   return multiply.outer(k, k)
pairwise_diff: return subtract.outer(asarray(a), asarray(b))
               (same as a[:, None] - b[None, :])
```
