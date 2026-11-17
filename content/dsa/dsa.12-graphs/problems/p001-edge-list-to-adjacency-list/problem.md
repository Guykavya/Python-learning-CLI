# Edge list to adjacency list

Graphs usually arrive as an **edge list**: the number of vertices `n` (numbered `0 .. n-1`) and a list of pairs `(u, v)`. Almost every algorithm in this module wants an **adjacency list** instead: for each vertex, the list of its neighbours (chapter section 2).

Write `build_adj(n, edges, directed=False)`. It returns a list of `n` lists. `adj[u]` holds the neighbours of `u`.

Rules:

- **Order = edge-list order.** Go through the edges in the order they are listed. For an edge `(u, v)` append `v` to `adj[u]`; if the graph is undirected, also append `u` to `adj[v]`. Later problems (BFS and DFS orders) depend on this order, so the tests check it exactly.
- If `directed=True`, the edge `(u, v)` goes only from `u` to `v`.
- Every vertex `0 .. n-1` has a list, also a vertex with no edges (its list is empty).
- A **self loop** `(u, u)` appears **once** in `adj[u]`, in both modes.
- Parallel edges (the same pair twice) appear twice: keep them.
- Every vertex must have its **own** list object.

## Example

```python
>>> build_adj(4, [(0, 1), (2, 0), (1, 2)])
[[1, 2], [0, 2], [0, 1], []]
>>> build_adj(3, [(0, 1), (2, 0)], directed=True)
[[1], [], [0]]
>>> build_adj(2, [(1, 1)])
[[], [1]]
```

In the first example, edge `(2, 0)` appends `0` to `adj[2]` and `2` to `adj[0]`. Vertex `3` has no edges and gets `[]`.

## Constraints

`0 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. `O(n + E)` time.
