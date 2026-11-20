# Floyd-Warshall

Write `floyd_warshall(n, edges)`. The graph has vertices `0 .. n-1` and **directed** edges `(u, v, w)`; weights may be negative, but the tests never contain a negative cycle. Return an `n x n` table (a list of `n` lists) where `dist[i][j]` is the shortest distance from `i` to `j`, `0` on the diagonal, and `float("inf")` when `j` cannot be reached from `i`.

This is chapter section 13: allow one more "middle" vertex `k` at a time, and the `k` loop must be the **outermost**.

Rules:

- Parallel edges: keep the **cheaper** one. Self loops with a non-negative weight do not change the diagonal (it stays 0).
- Return a new table; do not change `edges`. Every row must be a separate list.

## Example

```python
>>> floyd_warshall(4, [(0, 1, 3), (0, 2, 8), (1, 2, 2), (2, 3, 1), (3, 0, 2), (1, 3, 7)])
[[0, 3, 5, 6], [5, 0, 2, 3], [3, 6, 0, 1], [2, 5, 7, 0]]
```

`dist[0][3]` is 6: `0 -> 1 -> 2 -> 3` (`3 + 2 + 1`) beats `0 -> 1 -> 3` (`3 + 7`).

## Constraints

- `1 <= n <= 150`, `0 <= len(edges) <= n * n`, `-100 <= w <= 1000`. `O(V^3)` time.

## Think about

What does `dist[i][j]` mean after the round for `k`? Why does the order `for i: for j: for k:` give wrong answers, even though it tries every middle vertex for every pair?
