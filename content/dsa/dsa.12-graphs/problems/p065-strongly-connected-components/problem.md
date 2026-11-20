# Strongly connected components

Write `strongly_connected_components(n, edges)`. The graph is **directed**, with vertices `0 .. n-1` and edges `(u, v)`. Two vertices are in the same **strongly connected component** (SCC) when each can reach the other. Return the SCCs as a list of lists; every vertex appears in exactly one of them. The order of the components, and of the vertices inside one, does not matter: the tests check the partition.

Use Kosaraju's algorithm (chapter section 16) or Tarjan's. Graphs in the tests have up to `10**5` vertices on a single long chain, so a recursive DFS hits the recursion limit: **write the DFS without recursion** (the chapter's `finish_order` with an iterator stack shows how).

## Example

```python
>>> sorted(sorted(c) for c in strongly_connected_components(8,
...     [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3), (6, 5), (6, 7), (7, 6)]))
[[0, 1, 2], [3, 4, 5], [6, 7]]
>>> sorted(sorted(c) for c in strongly_connected_components(3, [(0, 1), (1, 2)]))
[[0], [1], [2]]
```

In the second graph nobody can come back, so every vertex is its own component.

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. Self loops and parallel edges can appear. `O(V + E)` time.

## Think about

Why does Kosaraju's second pass run on the **reversed** graph, and why in order of **decreasing** finish time? In Tarjan's algorithm, why must an edge to a vertex that is already in a finished component be ignored?
