# BFS order

Write `bfs_order(n, edges, start, directed=False)`. It returns the list of vertices in the order a **breadth-first search** from `start` visits them (chapter section 3).

Rules:

- Build the adjacency list in **edge-list order**: for an undirected edge `(u, v)` append `v` to `adj[u]` and `u` to `adj[v]`, in the order the edges are listed (problem p001; a self loop once). With `directed=True` the edge `(u, v)` only goes from `u` to `v`.
- Use a queue (`collections.deque`). When you take `u` from the queue, look at its neighbours **in adjacency order** and put every one that was never seen into the queue.
- Mark a vertex as seen **when you put it in the queue**, not when you take it out.
- Vertices that cannot be reached from `start` are **not** in the answer. `start` is always first.

## Example

```python
>>> bfs_order(6, [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)], 0)
[0, 2, 1, 3, 4]
>>> bfs_order(3, [(1, 0), (1, 2)], 0, directed=True)
[0]
```

Vertex 0's list is `[2, 1]` (the order of the edges), so `2` comes before `1`. Vertex 5 has no edges and is not reached. In the second example the edges leave `1`, so nothing can be reached from `0`.

## Constraints

`1 <= n <= 10**5`, up to `2 * 10**5` edges. `O(n + E)` time.
