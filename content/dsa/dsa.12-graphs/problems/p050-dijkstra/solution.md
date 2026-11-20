## Approach

Dijkstra settles vertices in order of distance. The heap gives the vertex with the smallest tentative distance; because all weights are non-negative, no later route can be shorter, so its distance is final. Its edges are relaxed: whenever `dist[u] + w` beats `dist[v]`, `dist[v]` drops and a new entry is pushed. Old entries stay in the heap (lazy deletion, dsa.11) and are skipped when they come out, because then `d > dist[u]`.

## Code

```python
import heapq


def dijkstra(n, edges, source):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    INF = float("inf")
    dist = [INF] * n
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                       # stale: a shorter route to u was already used
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist
```

## Complexity

Every edge pushes at most one entry, so the heap has at most `E + 1` entries: `O((V + E) log V)` time, `O(V + E)` memory.

## Another way

For a **dense** graph (`E` close to `V^2`) drop the heap: keep a `done` list and pick the closest unfinished vertex by scanning, `O(V^2)` in total. That beats the heap only when the graph is dense. A `done` set instead of the stale test also works when weights are non-negative: `if u in done: continue`.
