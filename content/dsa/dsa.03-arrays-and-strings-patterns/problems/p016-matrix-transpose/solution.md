## Approach

Output row `j` is input column `j`: walk down the input's rows and pick element `j` from each.

## Code

```python
r, c = map(int, input().split())
g = [input().split() for _ in range(r)]

for j in range(c):
    print(" ".join(g[i][j] for i in range(r)))
```

The values are never used as numbers, so they can stay as strings.

## Complexity

O(r * c) time and memory: every cell is read and printed once.

## Another way

`zip(*g)` passes the rows as separate arguments to `zip`, which then yields the first elements of all rows, then the
second elements, and so on: exactly the columns. `for col in zip(*g): print(*col)`. For a square grid you can also
transpose in place by swapping `g[i][j]` with `g[j][i]` for `j > i` only (swapping all pairs would swap everything
back).
