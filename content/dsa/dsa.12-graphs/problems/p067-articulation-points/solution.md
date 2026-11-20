## Approach

Removing `u` disconnects the subtree of a child `c` exactly when no back edge from that subtree reaches a proper ancestor of `u`: `low[c] >= tin[u]`. The root has no ancestors, so instead it counts its DFS children. The DFS is iterative with the same frames as the bridge finder.

## Code

```python
def articulation_points(n, edges):
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    tin = [-1] * n
    low = [0] * n
    timer = 0
    points = set()
    for s in range(n):
        if tin[s] != -1:
            continue
        tin[s] = low[s] = timer
        timer += 1
        root_children = 0
        stack = [(s, -1, iter(adj[s]))]
        while stack:
            u, via, it = stack[-1]
            step = next(it, None)
            if step is None:
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    low[p] = min(low[p], low[u])
                    if p != s and low[u] >= tin[p]:
                        points.add(p)
                continue
            v, i = step
            if i == via:
                continue
            if tin[v] == -1:
                tin[v] = low[v] = timer
                timer += 1
                if u == s:
                    root_children += 1
                stack.append((v, i, iter(adj[v])))
            else:
                low[u] = min(low[u], tin[v])
        if root_children >= 2:
            points.add(s)
    return sorted(points)
```

## Complexity

`O(V + E)` time and memory.

## Another way

The slow way: for each vertex, delete it and count the connected components of the rest with BFS; it is a cut vertex if the count of components (not counting itself) grew. `O(V (V + E))`, good for testing. The fast way can also build the **block-cut tree** (biconnected components) by keeping a stack of edges and popping a block whenever `low[c] >= tin[u]`.
