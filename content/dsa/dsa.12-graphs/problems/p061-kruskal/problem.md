# Kruskal

Write `kruskal(n, edges)`. The graph is **undirected** with vertices `0 .. n-1` and weighted edges `(u, v, w)`. Return the total weight of a **minimum spanning tree**: a set of `n - 1` edges that connects all vertices with the smallest possible total. If the graph is **not connected**, no spanning tree exists: return `None`.

Use Kruskal's algorithm (chapter section 15): sort the edges by weight, go from the cheapest to the most expensive, and take an edge when its two ends are **not yet connected**, as Union-Find (section 9) tells you.

Rules:

- Weights can be negative or zero. There may be parallel edges and self loops (a self loop never belongs to a tree).
- One vertex alone is a spanning tree with total `0`.
- Do not change `edges`.

## Example

```python
>>> kruskal(4, [(0, 1, 1), (1, 2, 4), (0, 2, 3), (2, 3, 2), (1, 3, 5)])
6
>>> kruskal(3, [(0, 1, 1)]) is None
True
```

Kruskal takes `0-1` (1), `2-3` (2), `0-2` (3) and skips the rest: total 6. In the second graph vertex 2 is cut off.

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`, `|w| <= 10**6`. `O(E log E)` time.

## Think about

Why is it safe to take the cheapest edge that does not close a cycle? How do you know at the end whether the graph was connected?
