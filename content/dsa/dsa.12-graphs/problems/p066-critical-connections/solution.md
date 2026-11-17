## Approach

A bridge is an edge that lies on no cycle. In a DFS tree, cycles come from back edges; `low[c]` records the highest point (smallest entry time) that the subtree of `c` can reach with one back edge. If even that is below `p` (`low[c] > tin[p]`), the only way from `c`'s subtree to the rest is the tree edge `p - c`. Skipping only the edge index we came by makes a parallel edge count as a back edge, so doubled cables are correctly not bridges.

## Code

```python
def critical_connections(n, edges):
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    tin = [-1] * n
    low = [0] * n
    timer = 0
    found = []
    for s in range(n):
        if tin[s] != -1:
            continue
        tin[s] = low[s] = timer
        timer += 1
        stack = [(s, -1, iter(adj[s]))]
        while stack:
            u, via, it = stack[-1]
            step = next(it, None)
            if step is None:
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    if low[u] < low[p]:
                        low[p] = low[u]
                    if low[u] > tin[p]:
                        found.append(edges[via])
                continue
            v, i = step
            if i == via:
                continue
            if tin[v] == -1:
                tin[v] = low[v] = timer
                timer += 1
                stack.append((v, i, iter(adj[v])))
            elif tin[v] < low[u]:
                low[u] = tin[v]
    return found
```

## Complexity

Every vertex and every edge is handled a constant number of times: `O(V + E)` time and memory.

## Another way

**Count the back edges over each tree edge.** After an iterative DFS, every non-tree edge `(a, b)` with `b` an ancestor of `a` covers the tree edges on the path from `a` up to `b`. Add `+1` at `a` and `-1` at `b`, then sum these marks bottom-up over the tree (children before parents, for example in reverse preorder): a tree edge `parent(c) - c` is a bridge exactly when the sum for `c`'s subtree is 0. The slow way, for checking: remove each edge in turn and test with BFS whether its two ends are still connected, `O(E (V + E))`.
