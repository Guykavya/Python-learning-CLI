## Hint 1

Removing an edge that lies on a cycle never disconnects anything: the rest of the cycle is a detour. So the bridges are the edges on **no** cycle. In a DFS tree, every non-tree edge closes a cycle with the tree path between its ends. A tree edge `p - c` is on a cycle only if some back edge goes from `c`'s subtree to `p` or above. How can one number per vertex record "how high can my subtree climb"?

## Hint 2

Store `adj[u]` as pairs `(v, edge_index)`. In the DFS, when you look at `(v, i)` from `u`: if `i` is the edge you arrived by, skip it; if `v` was already visited, `low[u] = min(low[u], tin[v])`; otherwise `v` is a child. When a child `c` finishes, its parent `p` does `low[p] = min(low[p], low[c])` and checks `low[c] > tin[p]`.

## Hint 3

Without recursion, keep frames `(u, index of the edge we came by, iterator over adj[u])`:

```
for each unvisited s: tin[s] = low[s] = timer++;  stack = [(s, -1, iter(adj[s]))]
while stack:
    u, via, it = stack[-1];  step = next(it, None)
    if step is None:                                  # u finished
        stack.pop()
        if stack: p = stack[-1][0]; low[p] = min(low[p], low[u]); if low[u] > tin[p]: bridge edges[via]
        continue
    v, i = step
    if i == via: continue
    if tin[v] == -1: tin[v] = low[v] = timer++; stack.append((v, i, iter(adj[v])))
    else: low[u] = min(low[u], tin[v])
```
