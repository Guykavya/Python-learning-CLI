## Approach

Build the rows with a comprehension so that each is a separate list, then set one or two cells per edge. Going back, scan the whole table; for an undirected graph the matrix is symmetric, so only the upper triangle (with the diagonal, for self loops) is read, which lists each edge once.

## Code

```python
def to_matrix(n, edges, directed=False):
    m = [[0] * n for _ in range(n)]
    for u, v in edges:
        m[u][v] = 1
        if not directed:
            m[v][u] = 1
    return m


def to_edges(matrix, directed=False):
    n = len(matrix)
    out = []
    for u in range(n):
        start = 0 if directed else u
        for v in range(start, n):
            if matrix[u][v]:
                out.append((u, v))
    return out
```

## Complexity

`O(n^2)` memory for the matrix, always, even for a graph with no edges; `to_edges` must look at every cell: `O(n^2)`.

## Another way

For weighted graphs the cell holds the weight, and "no edge" is `float("inf")` (Floyd-Warshall, section 13) or `0` when weights are positive. A list of sets gives `O(1)` edge tests with only `O(n + E)` memory.
