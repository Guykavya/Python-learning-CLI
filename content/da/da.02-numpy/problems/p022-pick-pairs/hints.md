## Hint 1

What does `m[[0, 2], [1, 3]]` give: two values or four? And which two index arrays, used together, walk down the diagonal of the top-left `k × k` corner?

## Hint 2

```text
pick:            return matrix[rows, cols]          # NumPy pairs them up (and broadcasts their shapes)
diagonal_of_top: idx = np.arange(k)
                 return matrix[idx, idx]            # raises IndexError by itself if k is too big
```
