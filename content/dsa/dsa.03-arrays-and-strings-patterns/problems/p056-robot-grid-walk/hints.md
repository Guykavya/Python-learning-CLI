## Hint 1

How do you turn without sixteen `if` cases? Put the four directions in a list in **clockwise** order, `N E S W`, and keep
an index `d` into it. What does a right turn do to `d`? A left turn? (Remember `% 4`.)

## Hint 2

For direction `d`, the next cell is `(row + dr[d], col + dc[d])` with `dr = [-1, 0, 1, 0]` and `dc = [0, 1, 0, -1]`.
Before you move, check **all** of: the new row is in `0..r-1`, the new column is in `0..c-1`, and the cell is not `#`.
If any check fails, do nothing for this `F` and go on with the next command.

## Hint 3

```
convert the start to 0-based; d = 0 (N)
visited = set containing the start
for ch in commands:
    L: d = (d + 3) % 4      R: d = (d + 1) % 4
    F: nr, nc = row + dr[d], col + dc[d]
       if inside and grid[nr][nc] != '#': row, col = nr, nc; add to visited
print row + 1, col + 1, "NESW"[d]
print len(visited)
```
