## Approach

BFS from many sources at once: put all rotten oranges into the queue at distance 0. A level of the BFS is one minute. The fresh count tells us when to stop and whether some orange was unreachable. Turning a fresh orange into `2` when it is enqueued marks it as seen, so it is processed only once.

## Code

```python
from collections import deque


def minutes_to_rot(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    queue = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while queue and fresh:
        for _ in range(len(queue)):               # one minute = one BFS level
            r, c = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
        minutes += 1
    return minutes if fresh == 0 else -1
```

## Complexity

`O(rows * cols)` time and memory: every cell enters the queue at most once.

## Another way

Store `(r, c, minute)` in the queue instead of counting levels, and return the largest minute seen. It avoids the `for _ in range(len(queue))` loop, but you must still check at the end that no fresh orange is left.
