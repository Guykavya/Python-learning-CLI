## Hint 1

Find any land cell, then collect **all** cells of its island with a stack-based flood fill. Mark them as seen. These cells are the "sources": the bridge can start next to any of them.

## Hint 2

Put all cells of the first island in a queue with distance 0 (multi-source BFS). Expand through water one ring at a time. The first time you step onto a land cell that is **not** in the first island, it belongs to the second island. If that step leaves a cell at distance `d`, then the cells at distances `1..d` are water cells of the bridge: the answer is `d`.

## Hint 3

```
first = flood fill from the first '1' (stack), all marked seen
queue = deque((r, c, 0) for (r, c) in first)
while queue:
    r, c, d = queue.popleft()
    for each neighbour (nr, nc) inside the grid, not seen:
        if grid[nr][nc] == '1': return d          # reached the second island
        seen.add((nr, nc)); queue.append((nr, nc, d + 1))
```
