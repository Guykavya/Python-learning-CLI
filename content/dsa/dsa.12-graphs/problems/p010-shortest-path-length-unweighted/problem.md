# Shortest path length (unweighted)

In a graph without weights, the length of a path is its number of **edges**. BFS reaches every vertex for the first time along a shortest path (chapter section 3, "Why BFS gives the shortest path").

Write `distance(n, edges, s, t)` for an **undirected** graph with vertices `0 .. n-1`. It returns the number of edges on a shortest path from `s` to `t`:

- `0` if `s == t`;
- `-1` if `t` cannot be reached from `s`.

## Example

```python
>>> distance(5, [(0, 1), (1, 2), (2, 3), (0, 3)], 0, 2)
2
>>> distance(5, [(0, 1), (1, 2), (2, 3), (0, 3)], 0, 4)
-1
>>> distance(3, [(0, 1)], 2, 2)
0
```

`0 -> 1 -> 2` and `0 -> 3 -> 2` both have two edges. Vertex 4 has no edges.

## Constraints

`1 <= n <= 10**5`, up to `2 * 10**5` edges. `O(n + E)` time.
