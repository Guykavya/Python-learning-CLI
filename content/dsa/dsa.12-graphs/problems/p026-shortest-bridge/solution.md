## Approach

The question is "how far apart are the two islands", where a step through water costs one flipped cell. Distance between two **sets** of cells is a job for multi-source BFS: start from every cell of one set at once, and the first ring that touches the other set gives the distance.

Step 1 finds the first island. We scan for any `'1'` and flood-fill its island with an explicit stack (the cells are marked as seen when they are pushed, as in chapter section 3's "mark when you push").

Step 2 puts all those cells into a queue with distance 0 and runs BFS. A water cell reached from a cell at distance `d` gets distance `d + 1`: it would be the `(d + 1)`-th flipped cell. When a step leads onto land that is not in the first island, the bridge is complete. The cell we stepped from is at distance `d`, so exactly `d` water cells lie on the bridge.

```python
from collections import deque


def shortest_bridge(grid):
    rows, cols = len(grid), len(grid[0])
    steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
    start = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == "1")
    seen = {start}
    stack, first = [start], []
    while stack:                                   # flood fill of the first island
        r, c = stack.pop()
        first.append((r, c))
        for dr, dc in steps:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen and grid[nr][nc] == "1":
                seen.add((nr, nc))
                stack.append((nr, nc))
    queue = deque((r, c, 0) for r, c in first)     # multi-source BFS
    while queue:
        r, c, d = queue.popleft()
        for dr, dc in steps:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen:
                if grid[nr][nc] == "1":
                    return d                       # the second island
                seen.add((nr, nc))
                queue.append((nr, nc, d + 1))
    return -1                                      # not reached: fewer than two islands
```

## Complexity

Every cell is pushed at most once in each phase: `O(rows * cols)` time and memory.

## Another way

Run the BFS in "rings": keep a list `frontier`, and in each round build the next frontier from all neighbours of the current one, counting rounds. Or flip the roles and BFS from the second island: the answer is the same. A slow but correct check on small grids: the answer is the smallest Manhattan distance between a cell of one island and a cell of the other, minus one (there are no obstacles, so a straight staircase path works). That is `O(A * B)` for islands of sizes `A` and `B`, which is what the time-limit test rejects.
