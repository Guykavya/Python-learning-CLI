# Articulation points

The graph is **undirected**, with vertices `0 .. n-1` and edges `(u, v)`. A vertex is an **articulation point** (a cut vertex) if removing it, together with its edges, splits the part of the graph it belongs to into more pieces. Write `articulation_points(n, edges)`: the sorted list of articulation points.

Use the same low-link DFS as for bridges (chapter section 17), with two rules:

- a **non-root** vertex `u` is an articulation point if it has a DFS child `c` with `low[c] >= tin[u]` (the subtree of `c` cannot climb **above** `u`);
- the **root** of a DFS tree is an articulation point exactly when it has **two or more** DFS children.

The tests include a line of `10**5` vertices: write the DFS **without recursion**.

## Example

```python
>>> articulation_points(5, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4)])
[1, 3]
>>> articulation_points(3, [(0, 1), (1, 2), (2, 0)])
[]
```

Removing 1 cuts `{0, 2}` from `{3, 4}`; removing 3 cuts off 4. A triangle has no articulation point.

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`, no self loops (parallel edges may appear). The graph may be disconnected. `O(V + E)` time.

## Think about

Why `>=` here but `>` for bridges? Why does the root need its own rule: what would the normal rule say about the root of every tree?
