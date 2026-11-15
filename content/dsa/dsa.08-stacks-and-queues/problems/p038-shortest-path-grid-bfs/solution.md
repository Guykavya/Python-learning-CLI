## Approach

BFS explores the grid in rings: first every cell at distance 1, then every cell at distance 2, and so on, because the queue hands out cells in the order they were found. So the first time the goal comes out of the queue, it has its smallest distance. Each cell is marked when it is enqueued, so it enters the queue at most once.

## Code

```python
from collections import deque


def shortest_path(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    if grid[start[0]][start[1]] == "#" or grid[goal[0]][goal[1]] == "#":
        return -1
    queue = deque([(start[0], start[1], 0)])
    seen = {start}
    while queue:
        r, c, steps = queue.popleft()
        if (r, c) == goal:
            return steps
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#" and (nr, nc) not in seen:
                seen.add((nr, nc))                 # mark when we ENQUEUE
                queue.append((nr, nc, steps + 1))
    return -1
```

## Complexity

`O(rows * cols)` time and memory: every cell is enqueued at most once and has 4 neighbours to check.

## Another way

Keep a `dist` grid filled with `-1` instead of the `seen` set: `dist[start] = 0`, and a cell is new when its `dist` is `-1`. The queue then holds only `(row, col)`. This also gives you the distance to **every** reachable cell, which is handy when several goals are asked about.
