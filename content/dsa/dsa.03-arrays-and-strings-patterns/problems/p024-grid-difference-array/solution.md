## Approach

The 2D prefix sum of a single `+v` at `(r1, c1)` adds `v` to the whole quarter-plane below and to the right of
that cell. Four marks carve that quarter-plane down to exactly the rectangle:

```
+v at (r1, c1)        -v at (r1, c2+1)
-v at (r2+1, c1)      +v at (r2+1, c2+1)
```

Each update costs O(1). After all updates, one 2D prefix sum over the marks gives every cell its final value.
The grid `D` gets one spare row and column so that `r2 + 1` and `c2 + 1` never fall outside it.

## Code

```python
r, c, q = [int(x) for x in input().split()]

# D has one spare row and column, so the marks at r2 + 1 and c2 + 1 always fit.
D = [[0] * (c + 2) for _ in range(r + 2)]
for _ in range(q):
    r1, c1, r2, c2, v = [int(x) for x in input().split()]
    D[r1][c1] += v
    D[r1][c2 + 1] -= v
    D[r2 + 1][c1] -= v
    D[r2 + 1][c2 + 1] += v

# 2D prefix sum of the marks gives the final value of every cell.
out = []
above = [0] * (c + 2)
for i in range(1, r + 1):
    row_sum = 0
    current = [0] * (c + 2)
    for j in range(1, c + 1):
        row_sum += D[i][j]
        current[j] = above[j] + row_sum
    out.append(" ".join(str(current[j]) for j in range(1, c + 1)))
    above = current
print("\n".join(out))
```

The marks for the example, rows 1–3 and columns 1–5 (row 4 also holds marks, but no output row reads it):

```
 5   0   0  -5   0      update 1: +5 at (1,1), -5 at (1,4); its -5 at (3,1) and +5 at (3,4) are below
 0  -2   0   0   2      update 2: -2 at (2,2), +2 at (2,5)
 2  -7   0   5   0      (3,1) = -5 + 7 = 2, (3,2) = -7 (update 3), (3,4) = +5 (update 1)
```

Row 1 running sums: `5 5 5 0`. Row 2 running sums `0 -2 -2 -2`, plus the row above: `5 3 3 -2`. Row 3 running sums
`2 -5 -5 0`, plus the row above: `7 -2 -2 -2`. Those are the three output rows.

## Complexity

O(q + r*c) time and O(r*c) memory. Updating cell by cell costs up to O(q * r * c).

## Another way

Keep a 1D difference array per row: each update marks `+v` at `c1` and `-v` at `c2 + 1` in rows `r1..r2`. That is
O(rows) per update, so O(q * r + r * c) in total. It is simpler to get right, but slower when the rectangles are tall.
