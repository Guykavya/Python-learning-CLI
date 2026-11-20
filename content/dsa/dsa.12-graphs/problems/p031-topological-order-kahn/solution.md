## Approach

A vertex can be placed when everything that must come before it is already placed, that is, when its remaining in-degree is 0. Kahn's algorithm (chapter section 7) keeps exactly those vertices in a queue. Placing a vertex removes its outgoing edges, which may free more vertices.

If the graph has a cycle, no vertex on it ever reaches in-degree 0: each one waits for its predecessor on the cycle. The vertices reachable from the cycle wait for them. So they never enter the order, and `len(order) < n` is a complete cycle test.

Parallel edges are fine as long as the in-degree counts every listed edge (the same edge gives two decrements later). A self loop gives its vertex an in-degree that only the vertex itself could lower, so it is stuck: a cycle.

```python
from collections import deque


def topo_kahn(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    ready = deque(v for v in range(n) if indeg[v] == 0)
    order = []
    while ready:
        u = ready.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    return order if len(order) == n else []
```

## Complexity

Every vertex enters the queue at most once and every edge is followed once: `O(n + E)` time and memory.

## Another way

A DFS that records each vertex when it is **finished** and reverses that list (the next problem, p032). Or use a min-heap instead of the queue to get the **smallest** order in dictionary order (chapter section 7, "The smallest order"), at `O((n + E) log n)`.
