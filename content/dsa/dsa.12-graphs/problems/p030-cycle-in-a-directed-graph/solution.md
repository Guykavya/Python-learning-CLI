## Approach

During a DFS, the vertices that are entered but not finished form exactly the current path from the start vertex. An edge from the current vertex to a vertex on this path closes a directed cycle. An edge to a vertex that is already finished cannot: everything reachable from a finished vertex was explored, and if a way back to the current path existed, the cycle would have been found then. So we need three states (chapter section 6), not two.

To survive a chain of 100,000 vertices we keep the DFS on an explicit stack of `(vertex, iterator)` pairs, the same trick as the iterative topological sort of chapter section 7: each step takes one more neighbour of the vertex on top; when it has none left, the vertex is finished.

```python
WHITE, GREY, BLACK = 0, 1, 2


def has_cycle_directed(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    colour = [WHITE] * n
    for s in range(n):
        if colour[s] != WHITE:
            continue
        colour[s] = GREY
        stack = [(s, iter(adj[s]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                colour[u] = BLACK                  # finished: no cycle through u
                stack.pop()
            elif colour[v] == GREY:
                return True                        # back edge to the current path
            elif colour[v] == WHITE:
                colour[v] = GREY
                stack.append((v, iter(adj[v])))
    return False
```

A self loop `(u, u)` is found at once: `u` is GREY when its own edge is looked at.

## Complexity

Every vertex is entered once and every edge is followed once: `O(n + E)` time, `O(n)` for the colours and the stack.

## Another way

Kahn's algorithm (chapter section 7): repeatedly remove vertices with in-degree 0. If some vertices are never removed, they lie on or behind a cycle, so `len(order) < n` means "cycle". It needs no DFS at all and is naturally iterative.
