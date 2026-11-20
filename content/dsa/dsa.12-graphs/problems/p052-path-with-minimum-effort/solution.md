## Approach

Dijkstra's proof needs one thing: extending a route never makes it cheaper. With a non-negative weight, `max(e, w) >= e`, just like `e + w >= e`. So the cell with the smallest effort in the heap is final when it is popped, and the same algorithm works with `max` in place of `+`. This kind of path is a **minimax** (bottleneck) path.

## Code

```python
import heapq


def minimum_effort(heights):
    rows, cols = len(heights), len(heights[0])
    INF = float("inf")
    best = [[INF] * cols for _ in range(rows)]
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        e, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return e
        if e > best[r][c]:
            continue
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols:
                ne = max(e, abs(heights[r][c] - heights[nr][nc]))
                if ne < best[nr][nc]:
                    best[nr][nc] = ne
                    heapq.heappush(heap, (ne, nr, nc))
    return 0
```

## Complexity

`V = rows * cols` cells and about `4V` edges: `O(V log V)` time, `O(V)` memory.

## Another way

**Binary search on the answer** (dsa.06): "can I reach the corner using only steps with difference `<= x`?" is a plain BFS, and the answer is monotone in `x`. Search `x` over the sorted distinct differences: `O(V log V)` as well. A third way is the MST fact of chapter section 15: add the edges in increasing order with Union-Find and stop when the two corners join; the last edge added is the answer.
