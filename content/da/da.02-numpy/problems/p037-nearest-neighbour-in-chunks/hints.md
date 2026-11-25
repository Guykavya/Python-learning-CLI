## Hint 1

Start from the chapter's broadcast table (Ch. 11.7) for a **block** of rows: `block = points[start:start + chunk]` against all `points` gives a `(len(block), n)` table. Which entries of that table are the distances of a point to itself? (Row `r` of the block is point number `start + r`.)

## Hint 2

Set those self-entries to `np.inf` with fancy indexing (Ch. 9): `table[rows, start + rows] = np.inf` with `rows = np.arange(len(block))`. Then the row minimum is the nearest other point. Note: the last block can be shorter than `chunk`.

## Hint 3

```text
check n >= 2 and chunk >= 1
best = empty(n)
for start in range(0, n, chunk):
    block = points[start:start + chunk]
    d2 = ((block[:, None, :] - points[None, :, :]) ** 2).sum(axis=-1)
    rows = arange(len(block));  d2[rows, start + rows] = inf
    best[start:start + len(block)] = d2.min(axis=1)
return sqrt(best)
```
