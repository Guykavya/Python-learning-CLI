# Transpose a directed graph

The **transpose** (or reverse) of a directed graph has every edge turned around: `u -> v` becomes `v -> u`. It answers the backwards question: "from which vertices can I **reach** `t`?" is the same as "which vertices can `t` reach in the transpose?". Kosaraju's algorithm for strongly connected components (section 16) uses it.

Write two functions. The graph is given as an adjacency list `adj` (a list of `n` lists, as built in p001 with `directed=True`).

1. `transpose(adj)` returns the adjacency list of the transpose. **Order:** go through `u = 0, 1, ..., n-1`, and for each `u` through `adj[u]` in its order; for each `v` found, append `u` to `rev[v]`. Parallel edges and self loops are kept. Do not change `adj`.
2. `can_reach(adj, target)` returns the **sorted** list of all vertices that can reach `target` by following edges forwards (zero or more edges, so `target` itself is in the list). Use the transpose and one BFS: `O(n + E)`.

## Example

```python
>>> adj = [[1, 2], [2], [], [2]]          # 0->1, 0->2, 1->2, 3->2
>>> transpose(adj)
[[], [0], [0, 1, 3], []]
>>> can_reach(adj, 2)
[0, 1, 2, 3]
>>> can_reach(adj, 1)
[0, 1]
```

## Constraints

`1 <= n <= 10**5`, up to `2 * 10**5` edges. Both functions `O(n + E)`; the tests use a chain of 100,000 vertices, so use BFS or an explicit stack, not recursion.
