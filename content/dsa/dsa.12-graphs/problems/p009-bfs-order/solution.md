## Approach

Build the adjacency list in input order, then run the chapter's BFS: `popleft`, record the vertex, push unseen neighbours in order and mark them at once.

## Code

```python
from collections import deque


def bfs_order(n, edges, start, directed=False):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        if not directed and u != v:
            adj[v].append(u)
    seen = {start}
    queue = deque([start])
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return order
```

## Complexity

`O(n + E)`: every reachable vertex enters the queue once, and each edge is looked at once from each end.

## Another way

A list of booleans `seen = [False] * n` is a little faster than a set when the vertices are `0 .. n-1`. Marking on pop gives the same order here but lets a vertex sit in the queue many times (chapter: 19,901 pushes instead of 200 on a complete graph).
