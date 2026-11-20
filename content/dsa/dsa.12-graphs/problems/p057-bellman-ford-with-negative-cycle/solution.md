## Approach

`V - 1` rounds make every real shortest distance final. If an `V`-th pass over the edges can still lower a distance, the route to that vertex can be made shorter forever, which only a negative cycle allows; and because only finite distances are relaxed, that cycle is reachable from the source.

## Code

```python
def bellman_ford(n, edges, source):
    INF = float("inf")
    dist = [INF] * n
    dist[source] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break                       # nothing moved: the distances are final
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return None
    return dist
```

The early `break` is safe: a round without changes means no later round can change anything, and the check round then finds nothing either.

## Complexity

`O(V * E)` time, `O(V)` memory.

## Another way

**SPFA with counting**: keep a queue of vertices whose distance changed and only relax their edges; if a vertex is relaxed `V` times (or a route reaches `V` edges), there is a negative cycle. Often faster, same worst case. To decide whether a negative cycle exists **anywhere**, start with `dist = [0] * n` (a virtual source with 0-edges to every vertex) instead.
