## Approach

Choosing `r` items out of `n`: either the last item is chosen (then choose `r - 1` from the other `n - 1`) or it is
not (choose `r` from the other `n - 1`). This gives `C(n, r) = C(n-1, r-1) + C(n-1, r)`. Building the table row by
row computes each value exactly once.

## Code

```python
rows = [[1]]
for n in range(1, 61):
    prev = rows[n - 1]
    row = [1]
    for r in range(1, n):
        row.append(prev[r - 1] + prev[r])
    row.append(1)
    rows.append(row)

q = int(input())
for _ in range(q):
    n, r = (int(x) for x in input().split())
    print(rows[n][r] if r <= n else 0)
```

## Complexity

The table has about `60 * 60 / 2 = 1800` entries, built once. Each query is O(1). Plain recursion without a table
makes about `C(n, r)` calls (hundreds of quadrillions for `(60, 30)`).

## Another way

Multiplicative formula with exact division: `c = 1; for i in range(1, r + 1): c = c * (n - r + i) // i`. After each step `c`
is itself a binomial coefficient, so the division is always exact. This needs no table, costs O(r), and works for
bigger `n` (Python ints are exact). Another option is recursion with memoisation (`functools.lru_cache`).
