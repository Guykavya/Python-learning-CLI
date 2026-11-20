## Approach

Every edge contributes one to each of its two ends. Count with lists of zeros, one pass over the edges.

## Code

```python
def degrees(n, edges, directed=False):
    if directed:
        indeg, outdeg = [0] * n, [0] * n
        for u, v in edges:
            outdeg[u] += 1
            indeg[v] += 1
        return indeg, outdeg
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    return deg
```

## Complexity

`O(n + E)` time, `O(n)` memory.

## Another way

From an adjacency list, `len(adj[u])` is the degree, as long as self loops are stored twice (or added by hand). In-degrees are what Kahn's topological sort (section 7) starts from. The handshake lemma also proves that the number of vertices with **odd** degree is always even.
