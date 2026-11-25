## Hint 1

What is the shape of `x.sum(axis=1)` for a `(3, 2)` table, and can it be divided into `x`? Which keyword keeps the reduced axis as length 1? Then: how can a division skip the places where the total is 0, so it never computes `0 / 0`?

## Hint 2

```text
x = x as float
totals = x.sum(axis=1, keepdims=True)                  # shape (rows, 1)
out = np.zeros(x.shape)                                # zeros stay where we skip
np.divide(x, totals, out=out, where=totals != 0)       # only divide where the total is not 0
return out
```
