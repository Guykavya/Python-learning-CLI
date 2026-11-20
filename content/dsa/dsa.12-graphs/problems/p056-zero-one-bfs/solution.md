## Approach

The deque plays the role of Dijkstra's heap. Its front always holds a vertex with the smallest tentative distance: a 0-edge gives the same distance and is put in front, a 1-edge gives `d + 1` and goes behind the current wave. Because a distance can still drop after a vertex was first reached, we relax with a comparison instead of a seen flag.

## Code

```python
from collections import deque


def zero_one_bfs(n, edges, source):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    INF = float("inf")
    dist = [INF] * n
    dist[source] = 0
    dq = deque([source])
    while dq:
        u = dq.popleft()
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                if w == 0:
                    dq.appendleft(v)
                else:
                    dq.append(v)
    return dist
```

## Complexity

Every vertex enters the deque a constant number of times (at most once per distance value it gets, and its distance can drop only from `d + 1` to `d`): `O(V + E)` time, `O(V + E)` memory.

## Another way

Dijkstra with a heap gives the same distances in `O((V + E) log V)`. For weights `0` and `k` the same deque trick works; for weights `1` and `2`, split each 2-edge into two 1-edges with a new middle vertex and run plain BFS.
