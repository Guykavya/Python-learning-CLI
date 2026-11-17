# Is the graph bipartite?

An undirected graph is **bipartite** if its vertices can be split into two teams so that every edge joins two vertices of **different** teams (chapter section 8).

Write `is_bipartite(n, edges)` for vertices `0 .. n-1` and a list of undirected edges `(u, v)`. Return `True` or `False`.

Use two-colouring with BFS, as in the chapter: give a start vertex colour 0, give each neighbour the opposite colour, and if an edge ever joins two vertices of the **same** colour, the answer is `False`. The graph can have several pieces: colour **each** piece, starting from every vertex that has no colour yet.

A self loop `(u, u)` joins `u` with itself, so a graph with a self loop is not bipartite.

## Example

```python
>>> is_bipartite(4, [(0, 1), (1, 2), (2, 3), (3, 0)])   # a square (even cycle)
True
>>> is_bipartite(3, [(0, 1), (1, 2), (2, 0)])           # a triangle (odd cycle)
False
>>> is_bipartite(5, [(0, 1), (2, 3), (3, 4), (4, 2)])   # the triangle is in the second piece
False
>>> is_bipartite(3, [])
True
```

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. A path of 100,000 vertices is in the tests: no recursion.

## Think about

Why does a cycle of odd length make two colours impossible, while an even cycle is fine?
