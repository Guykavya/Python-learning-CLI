# Critical connections (bridges)

A network has `n` servers `0 .. n-1` and **undirected** cables `edges = [(u, v), ...]`. A cable is **critical** (a **bridge**) if removing it leaves some two servers that can no longer reach each other, which were connected before.

Write `critical_connections(n, edges)`: the list of critical cables, each written exactly as it appears in `edges`, in any order.

Use the low-link DFS of chapter section 17: `tin[u]` is the entry time of `u`, `low[u]` the smallest entry time reachable from `u`'s subtree with one back edge. The tree edge from `p` to its child `c` is a bridge exactly when `low[c] > tin[p]`.

Two traps from the chapter:

- **Parallel cables**: if `u` and `v` are joined by two cables, neither is a bridge. Skip only the **edge you came by** (its index), not every edge back to the parent vertex.
- **Deep graphs**: the tests include a line of `10**5` servers, so the DFS must be written **without recursion** (section 17, "Without recursion").

## Example

```python
>>> sorted(critical_connections(4, [(0, 1), (1, 2), (2, 0), (1, 3)]))
[(1, 3)]
>>> critical_connections(2, [(0, 1), (0, 1)])
[]
```

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`, no self loops. The graph may be disconnected. `O(V + E)` time.

## Think about

Why does `low[c] > tin[p]` mean "nothing below `c` can climb back to `p` or above without this edge"? Why `>` and not `>=` (which is the rule for articulation points)?
