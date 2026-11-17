## Hint 1

Write the moves as a list of `(dr, dc)` pairs in the required order. For each one, compute `nr, nc` and keep the cell only if it is inside **and** open. What does `grid[-1]` give in Python? Why does that make the "inside" check important for the top row and the left column?

## Hint 2

```
moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
if diagonal: moves += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
out = []
for dr, dc in moves:
    nr, nc = r + dr, c + dc
    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
        out.append((nr, nc))
```
