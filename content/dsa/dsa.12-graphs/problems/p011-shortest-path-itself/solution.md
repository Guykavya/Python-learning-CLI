## Approach

Run BFS from `s` and store `parent[v]` the first time `v` is seen. The parent links form the BFS tree; the tree path from `s` to `t` is a shortest path. Walk it backwards from `t` with a loop and reverse it.

## Code

```python
from collections import deque


def shortest_path(n, edges, s, t):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent = {s: None}
    queue = deque([s])
    while queue:
        u = queue.popleft()
        if u == t:
            break
        for v in adj[u]:
            if v not in parent:
                parent[v] = u
                queue.append(v)
    if t not in parent:
        return None
    path = []
    x = t
    while x is not None:
        path.append(x)
        x = parent[x]
    path.reverse()
    return path
```

## Complexity

`O(n + E)` for the BFS and `O(length)` to rebuild the path.

## Another way

Run the BFS from `t` instead: then the parent links point **towards** `t`, and walking from `s` gives the path in the right order without reversing. Storing a whole path per vertex in the queue also works, but it copies lists and costs `O(n^2)` memory on a long path.
