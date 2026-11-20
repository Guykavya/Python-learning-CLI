# Prim

Write `prim(n, edges)`. The graph is **undirected** with vertices `0 .. n-1` and weighted edges `(u, v, w)`. Grow a minimum spanning tree from vertex **0** with Prim's algorithm (chapter section 15): a heap holds the edges that leave the tree, and each step adds the **cheapest** one whose far end is not in the tree yet.

Return a pair `(total, tree)`:

- `tree` is the list of the `n - 1` tree edges **in the order they were added**, each written `(u, v, w)` with `u` already in the tree and `v` the new vertex;
- `total` is the sum of their weights.

If the graph is not connected, return `None`. With `n = 1` return `(0, [])`.

Because the order is part of the answer, the tests check that every edge you add is a cheapest edge leaving the tree at that moment (with equal weights, any of the cheapest is fine).

## Example

```python
>>> prim(4, [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 5), (2, 3, 8)])
(8, [(0, 2, 1), (2, 1, 2), (1, 3, 5)])
```

From `{0}` the cheapest way out is `0-2` (1); from `{0, 2}` it is `2-1` (2); from `{0, 2, 1}` it is `1-3` (5).

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. `O(E log V)` time. Weights can be negative. Do not change `edges`.

## Think about

Prim looks almost exactly like Dijkstra. What is the one difference in the key you push? What do you do when a popped edge leads to a vertex that is already in the tree?
