# Cycle in an undirected graph

Write `has_cycle(n, edges)`. The graph is **undirected**, with vertices `0 .. n-1` and an edge list `edges` of pairs `(u, v)`. Return `True` if the graph contains a cycle, `False` otherwise.

Build the adjacency list in edge-list order (for `(u, v)` append `v` to `adj[u]` and `u` to `adj[v]`). Then search from every vertex that is not seen yet (the graph may have several pieces), as in chapter section 6.

The trap: in an undirected graph every edge `u - v` appears in both lists. When the search walks from `u` to `v`, it sees `u` again in `v`'s list. That is the edge it **came by**, not a cycle. Remember the vertex you came from and skip it.

Rules for the special cases:

- A **self loop** `(u, u)` is a cycle.
- **Two parallel edges** between the same two vertices (`(0, 1)` listed twice) form a cycle of length 2.
- A graph with no edges, or a forest of trees, has no cycle.

## Example

```python
>>> has_cycle(4, [(0, 1), (1, 2), (2, 3)])          # a path
False
>>> has_cycle(4, [(0, 1), (1, 2), (2, 0), (3, 3)])  # a triangle (and a self loop)
True
>>> has_cycle(2, [(0, 1), (0, 1)])                  # parallel edges
True
>>> has_cycle(6, [(0, 1), (2, 3), (3, 4), (4, 2)])  # the cycle is not in the piece of vertex 0
True
```

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. Use a stack, not recursion: a path of 100,000 vertices is in the tests.

## Think about

Why is "I already saw this vertex" enough to prove a cycle in an undirected graph, once you skip the edge you came by? Your search skips the parent in the child's list, so how is a pair of parallel edges still found? (Look at the parent's list.)
