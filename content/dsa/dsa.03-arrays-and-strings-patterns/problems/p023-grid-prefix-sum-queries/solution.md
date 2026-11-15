## Approach

`P[i][j]` stores the sum of the top-left `i x j` block. Building it uses the same inclusion-exclusion as the
queries: a cell's block is the cell, plus the block above, plus the block to the left, minus the block they
share. With a zero row and a zero column in front, every formula works at the edges too.

A query keeps the big block `(1,1)`–`(r2,c2)`, removes the rows above `r1` and the columns left of `c1`, and adds
back the top-left corner that was removed twice.

## Code

```python
r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]

# P[i][j] = sum of the top-left i rows and j columns. Row 0 and column 0 are all zeros.
P = [[0] * (c + 1) for _ in range(r + 1)]
for i in range(1, r + 1):
    row_sum = 0
    for j in range(1, c + 1):
        row_sum += grid[i - 1][j - 1]
        P[i][j] = P[i - 1][j] + row_sum

q = int(input())
out = []
for _ in range(q):
    r1, c1, r2, c2 = [int(x) for x in input().split()]
    s = P[r2][c2] - P[r1 - 1][c2] - P[r2][c1 - 1] + P[r1 - 1][c1 - 1]
    out.append(str(s))
print("\n".join(out))
```

The build uses a running `row_sum`: `P[i][j]` is the block above (`P[i-1][j]`) plus the first `j` cells of row
`i`. That is the same as the four-term formula, written with one subtraction fewer.

For the example:

```
P = 0  0  0  0  0
    0  1  3  6 10
    0  6 14 24 36
    0 15 33 54 78
```

Query `2 2 3 3`: `P[3][3] - P[1][3] - P[3][1] + P[1][1] = 54 - 6 - 15 + 1 = 34`.

Collecting the answers in a list and printing them with one `join` is much faster than 200000 `print` calls.

## Complexity

Build O(r * c), each query O(1): O(r*c + q) in total, and O(r*c) memory for `P`. Summing the cells of each
query is O(r * c) per query, up to 250000 * 200000 steps.

## Another way

Row prefix sums only: `R[i][j]` = sum of the first `j` cells of row `i`. A query then loops over its rows and
uses `R[i][c2] - R[i][c1-1]`, which is O(rows) per query. It is simpler, and good enough when `q` is small.
