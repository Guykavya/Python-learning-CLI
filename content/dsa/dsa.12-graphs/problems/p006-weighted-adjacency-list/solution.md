## Approach

Keep a dictionary per vertex. Each edge is a "maybe lower the value" update on one cell (directed) or on two cells (undirected). Because the undirected update always writes the same value into both directions, the two directions can never disagree.

## Code

```python
def weighted_adj(n, edges, directed=False):
    adj = [{} for _ in range(n)]

    def put(a, b, w):
        if b not in adj[a] or w < adj[a][b]:
            adj[a][b] = w

    for u, v, w in edges:
        put(u, v, w)
        if not directed:
            put(v, u, w)
    return adj
```

## Complexity

`O(n + E)` time and memory.

## Another way

`adj[a][b] = min(adj[a].get(b, w), w)` is the same update in one line. Dijkstra (section 10) works with parallel edges too, it just looks at more edges; removing them first makes the graph smaller. A list of `(v, w)` pairs (the chapter's `build_adj`) keeps all parallel edges.
