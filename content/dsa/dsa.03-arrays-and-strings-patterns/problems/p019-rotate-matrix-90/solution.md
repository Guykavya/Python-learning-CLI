## Approach

One clockwise turn = transpose + reverse every row. The transpose swaps only the pairs above the diagonal
(`j > i`), so each pair is swapped once. Turning the grid 4 times gives it back, so `k % 4` turns are enough.

## Code

```python
n, k = map(int, input().split())
g = [input().split() for _ in range(n)]

for _ in range(k % 4):
    for i in range(n):
        for j in range(i + 1, n):
            g[i][j], g[j][i] = g[j][i], g[i][j]
    for row in g:
        row.reverse()

for row in g:
    print(" ".join(row))
```

## Complexity

O(n^2) per turn and at most 3 turns: O(n^2) time. O(1) extra memory besides the grid (in place).

## Another way

Rotate ring by ring with 4-way swaps: for each layer and each offset, move top -> right -> bottom -> left -> top in
one step with a temporary variable. It is also in place and does each cell once per turn. With a new grid you can
write `[list(row) for row in zip(*g[::-1])]`: reverse the row order, then take columns. For `k % 4 == 2` you could
also reverse the row order and each row (a 180 degree turn) in one go.
