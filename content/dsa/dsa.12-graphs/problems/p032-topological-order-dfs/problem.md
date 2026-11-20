# Topological order (DFS)

Same task as p031, a different method. A directed edge `(u, v)` means "`u` must come before `v`". Write `topo_dfs(n, edges)` for vertices `0 .. n-1`: return a list of all vertices in an order where `u` comes before `v` for every edge, or `[]` if the graph has a cycle.

Use the **DFS way** of chapter section 7:

- run a DFS from every vertex that is not visited yet, following edges in the order they are listed;
- a vertex is **finished** when everything it points to has been explored; append it to a list `finished` at that moment;
- the **reverse** of `finished` is a topological order (a vertex finishes only after everything that must come after it);
- use the three colours of chapter section 6 (WHITE, GREY, BLACK): an edge to a GREY vertex means a cycle, so return `[]`.

Any valid order is accepted: the tests check it.

The graph can be a chain of 100,000 vertices. A recursive DFS gets a `RecursionError` there, so keep the DFS on an **explicit stack** of `(vertex, iterator over its neighbours)` pairs, like `topo_dfs` in the chapter.

## Example

```python
>>> topo_dfs(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
[0, 2, 1, 3]                 # finished = [3, 1, 2, 0], reversed
>>> topo_dfs(3, [(0, 1), (1, 2), (2, 0)])
[]
>>> topo_dfs(3, [(2, 1), (1, 0)])
[2, 1, 0]
```

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. `O(n + E)` time.

## Think about

Why is the order in which DFS **enters** the vertices (preorder) not a topological order? Find a two-edge graph where it fails.
