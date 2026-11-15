## Hint 1

Write down rows 0 to 5 of the triangle by hand. Each inner number is the sum of the two numbers above it.
How long is row `n`?

## Hint 2

Keep the rows in a list of lists: `rows[n][r]`. Start from `rows = [[1]]`. How do you build row `n` from
row `n - 1`? The first and last entries are 1.

## Hint 3

```
rows = [[1]]
for n from 1 to 60:
    prev = rows[n - 1]
    row = [1]
    for r from 1 to n - 1: row.append(prev[r - 1] + prev[r])
    row.append(1)
    rows.append(row)
for each query (n, r): print rows[n][r] if r <= n else 0
```
