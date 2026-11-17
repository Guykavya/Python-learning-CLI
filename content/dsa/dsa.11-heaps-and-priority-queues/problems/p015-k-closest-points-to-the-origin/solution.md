## Approach

Keep a **max**-heap of size `k` on the key `(distance, x, y)`: the root is the worst of the kept points, the one a closer point replaces. `heapq` is a min-heap, so store the negated key, `(-d, -x, -y)`: the smallest stored tuple is then the largest `(d, x, y)`. The ties at the border are decided by the whole tuple: a point replaces the root only when its negated key is **larger** than the root, that is, when its `(d, x, y)` is smaller. At the end, the heap holds the `k` best points in no useful order; sort these `k` entries by `(d, x, y)` and return the points.

## Code

```python
import heapq


def k_closest(points, k):
    if k <= 0:
        return []
    heap = []
    for point in points:
        x, y = point
        entry = (-(x * x + y * y), -x, -y)
        if len(heap) < k:
            heapq.heappush(heap, entry)
        elif entry > heap[0]:
            heapq.heapreplace(heap, entry)
    best = sorted((-nd, -nx, -ny) for nd, nx, ny in heap)
    return [(x, y) for _, x, y in best]
```

## Complexity

`O(n log k)` time for the scan, `O(k log k)` for the final sort of the `k` kept entries, `O(k)` memory.

## Another way

`sorted(points, key=lambda p: (p[0] * p[0] + p[1] * p[1], p))[:k]` is one line and `O(n log n)`. `heapq.nsmallest(k, points, key=...)` with the same key is the ready-made heap version. Quickselect finds the `k`-th smallest distance in `O(n)` on average. Do not use `math.sqrt` or `math.hypot`: with coordinates near `10**9` the squared distances `10**18` and `10**18 + 1` become the same float, and a tie is invented.
