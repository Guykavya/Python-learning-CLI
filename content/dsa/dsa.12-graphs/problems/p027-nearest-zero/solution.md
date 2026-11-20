## Approach

We want, for every cell, the distance to the **nearest** of many targets. Running one BFS per cell costs `O((rows * cols)^2)`. Turning it around is the multi-source trick (chapter section 3): BFS from all the zeros at once. BFS processes cells in order of distance, and a cell is first reached by the wave from the closest zero, so its first distance is the right one.

We keep a separate `dist` matrix (so `mat` stays unchanged), with `-1` for "not reached yet". Each cell gets its distance when it is **pushed**, which also marks it as seen.

```python
from collections import deque


def nearest_zero(mat):
    rows, cols = len(mat), len(mat[0])
    dist = [[-1] * cols for _ in range(rows)]
    queue = deque()
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                dist[r][c] = 0
                queue.append((r, c))
    while queue:
        r, c = queue.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                queue.append((nr, nc))
    return dist
```

## Complexity

Every cell is pushed and popped once: `O(rows * cols)` time and memory.

## Another way

Dynamic programming with two sweeps. A first pass from the top-left takes `min(itself, up + 1, left + 1)`; a second pass from the bottom-right takes `min(itself, down + 1, right + 1)`. Two passes are enough because every shortest path can be split into a part that goes up/left and a part that goes down/right. A single pass is **not** enough: it never looks down or right.
