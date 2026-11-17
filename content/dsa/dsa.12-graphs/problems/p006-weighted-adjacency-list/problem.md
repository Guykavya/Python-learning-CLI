# Weighted adjacency list

Road networks have **weights**: the edge `(u, v, w)` is a road of length `w`. The input sometimes lists the same pair twice with different lengths (two roads between the same towns). For shortest paths only the **shorter** road matters.

Write `weighted_adj(n, edges, directed=False)`. It returns a list of `n` dictionaries: `adj[u][v]` is the weight of the edge from `u` to `v`.

Rules:

- Vertices are `0 .. n-1`; every vertex gets a dictionary, maybe empty.
- Undirected: `(u, v, w)` is an edge in both directions, so `adj[u][v]` and `adj[v][u]` are both set. Directed: only `adj[u][v]`.
- **Parallel edges keep the smaller weight**: if the same pair (in the same direction) appears again, keep the minimum of the weights. In an undirected graph `(0, 1, 5)` and `(1, 0, 2)` are the same pair, so both `adj[0][1]` and `adj[1][0]` become `2`.
- A self loop `(u, u, w)` gives `adj[u][u]` (the smallest such `w`).
- Weights can be negative or zero.

## Example

```python
>>> weighted_adj(3, [(0, 1, 4), (1, 2, 1), (1, 0, 3)])
[{1: 3}, {0: 3, 2: 1}, {1: 1}]
>>> weighted_adj(2, [(0, 1, 7), (0, 1, 9)], directed=True)
[{1: 7}, {}]
```

## Constraints

`0 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. `O(n + E)` time.
