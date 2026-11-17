# Dijkstra

Write `dijkstra(n, edges, source)`. The graph has the vertices `0 .. n-1` and **directed** weighted edges `(u, v, w)`: a road from `u` to `v` of length `w`, with `w >= 0`. Return a **list** `dist` of length `n` where `dist[v]` is the length of the shortest route from `source` to `v`, or `float("inf")` if `v` cannot be reached.

This is the algorithm of chapter section 10: a heap of `(distance, vertex)` entries, settle the smallest, relax its edges, and skip **stale** entries (`d > dist[u]`) when they come out of the heap.

Rules:

- `dist[source]` is `0`.
- Edges are one-way. An undirected road is given as two edges, `(u, v, w)` and `(v, u, w)`.
- There may be **parallel edges** (the same `u, v` twice with different weights) and **self loops** (`u == v`). Weights can be `0`.
- Do not change the list `edges`.
- The neighbours of a vertex are the edges in the order they are listed (this does not change the answer, only the work).

## Example

```python
>>> edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5), (3, 4, 3)]
>>> dijkstra(6, edges, 0)
[0, 3, 1, 4, 7, inf]
```

The direct road `0 -> 1` costs 4, but `0 -> 2 -> 1` costs `1 + 2 = 3`. Vertex 5 has no roads at all, so its distance is `inf`.

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 3 * 10**5`, `0 <= w <= 10**4`.
- `O((V + E) log V)` time. The tests include a graph with `10**5` vertices and `3 * 10**5` edges, which must finish within a time limit (scanning all vertices to find the closest one, `O(V^2)`, is far too slow there).

## Think about

Why may a vertex be pushed more than once? Why is it wrong to call a vertex "done" when it is first **pushed**, and right when it is first **popped**?
