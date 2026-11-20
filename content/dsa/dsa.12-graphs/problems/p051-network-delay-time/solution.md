## Approach

The signal travels along every link at the same time, so it reaches each server at the length of the **shortest** route from `k`. All servers have the signal at the moment the last one gets it: the **maximum** shortest distance. If one distance is infinite, that server is never reached: `-1`. The only care points are the 1-based numbers and servers with no links.

## Code

```python
import heapq


def network_delay_time(times, n, k):
    adj = [[] for _ in range(n + 1)]
    for u, v, t in times:
        adj[u].append((v, t))
    INF = float("inf")
    dist = [INF] * (n + 1)
    dist[k] = 0
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, t in adj[u]:
            if d + t < dist[v]:
                dist[v] = d + t
                heapq.heappush(heap, (d + t, v))
    worst = max(dist[1:])
    return -1 if worst == INF else worst
```

## Complexity

`O((n + E) log n)` time, `O(n + E)` memory.

## Another way

With `n` this small, Bellman-Ford (`n - 1` rounds over all links, `O(n * E)`) also works, and it would still work with negative delays. For many queries from different start servers, Floyd-Warshall once (`O(n^3)`) and then a row maximum per query.
