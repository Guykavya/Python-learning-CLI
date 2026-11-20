## Approach

BFS from `s` with a `dist` dictionary that is also the "seen" record. The first time a vertex is reached, its distance is final, so we can stop as soon as `t` leaves the queue.

## Code

```python
from collections import deque


def distance(n, edges, s, t):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dist = {s: 0}
    queue = deque([s])
    while queue:
        u = queue.popleft()
        if u == t:
            return dist[u]
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return -1
```

## Complexity

`O(n + E)` time and `O(n)` memory in the worst case; often less, because the search stops at `t`.

## Another way

Stop even earlier: return `dist[u] + 1` the moment `t` is **pushed**. Bidirectional BFS (one search from `s`, one from `t`, stop when they meet) explores far fewer vertices on big graphs. With weights, BFS is not enough: section 10 (Dijkstra).
