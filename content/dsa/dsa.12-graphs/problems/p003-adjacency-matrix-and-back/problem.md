# Adjacency matrix and back

An **adjacency matrix** is an `n x n` table: `matrix[u][v]` is `1` if there is an edge from `u` to `v`, otherwise `0` (chapter section 2).

Write two functions:

1. `to_matrix(n, edges, directed=False)` returns the matrix as a list of `n` lists of `n` integers. For an undirected graph the matrix is symmetric: the edge `(u, v)` sets both `matrix[u][v]` and `matrix[v][u]`. A self loop `(u, u)` sets `matrix[u][u]`. Parallel edges give `1` (the matrix only says "there is an edge", not how many).
2. `to_edges(matrix, directed=False)` goes back to an edge list:
   - directed: every pair `(u, v)` with `matrix[u][v] == 1`;
   - undirected: every pair `(u, v)` with `u <= v` and `matrix[u][v] == 1` (each edge **once**);
   - in **row order**: `u` from `0` up, and inside a row `v` from small to large.

## Example

```python
>>> to_matrix(3, [(0, 1), (1, 2)])
[[0, 1, 0], [1, 0, 1], [0, 1, 0]]
>>> to_edges([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
[(0, 1), (1, 2)]
>>> to_matrix(2, [(1, 0)], directed=True)
[[0, 0], [1, 0]]
>>> to_edges([[0, 0], [1, 0]], directed=True)
[(1, 0)]
```

## Constraints

`0 <= n <= 300`. `to_matrix` is `O(n^2 + E)`, `to_edges` is `O(n^2)`.
