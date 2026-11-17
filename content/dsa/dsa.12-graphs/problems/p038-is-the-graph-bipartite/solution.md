## Approach

In a piece of the graph, once one vertex has a colour, every other colour is **forced**: each neighbour must get the opposite colour, their neighbours the opposite again, and so on. So we do not have to try colourings; we colour greedily with BFS (chapter section 8) and check every edge. If some edge has the same colour at both ends, no colouring can work, because all the choices were forced. Each piece is coloured on its own, so we start a BFS from every uncoloured vertex.

A self loop `(u, u)` puts `u` in its own list; `u` has the same colour as itself, so the check returns `False` without extra code.

```python
from collections import deque


def is_bipartite(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n
    for s in range(n):
        if colour[s] != -1:
            continue
        colour[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if colour[v] == -1:
                    colour[v] = 1 - colour[u]
                    queue.append(v)
                elif colour[v] == colour[u]:
                    return False                   # an edge inside one team
    return True
```

## Complexity

`O(n + E)`: every vertex is coloured once, every edge checked twice.

## Another way

Union-Find: for each vertex, all its neighbours must be in the **same** team. Unite every neighbour of `u` with the first neighbour of `u`; if `u` itself ever ends up in the same group as one of its neighbours, the graph is not bipartite. Or a DFS instead of BFS, with an explicit stack: the colours are forced in the same way.
