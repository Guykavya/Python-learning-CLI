## Walkthrough

Layer 0 (`first = 0`, `last = 3`), the outer ring:

| i | offset | top | right | bottom | left | old values (t, r, b, l) | new values (t, r, b, l) |
|---|---|---|---|---|---|---|---|
| 0 | 0 | (0,0) | (0,3) | (3,3) | (3,0) | 1, 4, 16, 13 | 13, 1, 4, 16 |
| 1 | 1 | (0,1) | (1,3) | (3,2) | (2,0) | 2, 8, 15, 9 | 9, 2, 8, 15 |
| 2 | 2 | (0,2) | (2,3) | (3,1) | (1,0) | 3, 12, 14, 5 | 5, 3, 12, 14 |

Layer 1 (`first = 1`, `last = 2`), the inner 2 x 2 ring:

| i | offset | top | right | bottom | left | old values | new values |
|---|---|---|---|---|---|---|---|
| 1 | 0 | (1,1) | (1,2) | (2,2) | (2,1) | 6, 7, 11, 10 | 10, 6, 7, 11 |

Each move rotates four cells that are each other's images under a quarter turn, so the moves never overlap: every
cell of the grid is in exactly one move (the 12 outer cells in three moves, the 4 inner cells in one).

## Output

```
layer 0 i 0: (0,0)=13 (0,3)=1 (3,3)=4 (3,0)=16
layer 0 i 1: (0,1)=9 (1,3)=2 (3,2)=8 (2,0)=15
layer 0 i 2: (0,2)=5 (2,3)=3 (3,1)=12 (1,0)=14
layer 1 i 1: (1,1)=10 (1,2)=6 (2,2)=7 (2,1)=11
13 9 5 1
14 10 6 2
15 11 7 3
16 12 8 4
```

## Key ideas

- A clockwise quarter turn sends `(r, c)` to `(c, n - 1 - r)`. The value 2 at `(0,1)` ends at `(1,3)`; 12 at `(2,3)`
  ends at `(3,1)`. Both match the output.
- A ring of side `k` needs `k - 1` moves, not `k`: the corner `(first, last)` is already the "right" cell of the
  move with `i = first`. Running `i` up to `last` would rotate the corners a second time.
- An `n x n` grid needs `n*n // 4` moves in total (for odd `n`, the centre cell stays put). Each move uses one
  temporary variable: O(1) extra memory.
