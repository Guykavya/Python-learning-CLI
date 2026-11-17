# Degrees

The **degree** of a vertex in an undirected graph is the number of edge ends that touch it. In a directed graph, the **in-degree** counts the edges that arrive at a vertex and the **out-degree** the edges that leave it (chapter section 1).

Write `degrees(n, edges, directed=False)`:

- undirected: return a list `deg` of length `n`, where `deg[u]` is the degree of `u`;
- directed: return a pair `(indeg, outdeg)` of two lists of length `n`.

Rules:

- Vertices are `0 .. n-1`; a vertex with no edges has degree `0`.
- Parallel edges count every time.
- A **self loop** `(u, u)` in an undirected graph adds **2** to `deg[u]`: both ends of the edge touch `u`. (So `len(adj[u])` from the previous problem is not always the degree.) In a directed graph it adds 1 to the in-degree and 1 to the out-degree of `u`.

Because every edge has two ends, the degrees of an undirected graph always add up to `2 * len(edges)` (the **handshake lemma**), and in a directed graph `sum(indeg) == sum(outdeg) == len(edges)`. The tests check both.

## Example

```python
>>> degrees(4, [(0, 1), (0, 2), (1, 2), (2, 3)])
[2, 2, 3, 1]
>>> degrees(3, [(0, 1), (0, 2), (2, 0)], directed=True)
([1, 1, 1], [2, 0, 1])
>>> degrees(2, [(0, 0)])
[2, 0]
```

## Constraints

`0 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. `O(n + E)`; you do not need an adjacency list.
