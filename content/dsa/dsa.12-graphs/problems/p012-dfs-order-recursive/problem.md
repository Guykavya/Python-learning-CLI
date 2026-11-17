# DFS order (recursive)

**Depth-first search** walks forward as long as there is an unvisited neighbour, and backs up only at a dead end (chapter section 4). The recursive version is the shortest to write.

Write `dfs_order(n, edges, start)` for an **undirected** graph with vertices `0 .. n-1`, using **recursion**. It returns the vertices in the order DFS first visits them.

Rules:

- Build the adjacency list in **edge-list order**: for an undirected edge `(u, v)` append `v` to `adj[u]` and `u` to `adj[v]`, in the order the edges are listed (problem p001; a self loop once).
- When you visit `u`, mark it, record it, then go through `adj[u]` **in order** and visit (recursively) every neighbour that is not yet visited.
- Unreachable vertices are not in the answer. `start` is first.

The tests here use small graphs only (at most a few hundred vertices). Problem p013 asks for a version without recursion that works on 100,000 vertices.

## Example

```python
>>> dfs_order(5, [(0, 1), (0, 2), (1, 3), (3, 2), (1, 4)], 0)
[0, 1, 3, 2, 4]
```

From `0` the first neighbour is `1`; from `1` the first unvisited neighbour is `3`; from `3` it is `2`. `2` has no unvisited neighbour, so the search backs up to `3`, then to `1`, whose next neighbour `4` is visited last. BFS from `0` would give `[0, 1, 2, 3, 4]`.

## Constraints

`1 <= n <= 300`. `O(n + E)` time.
