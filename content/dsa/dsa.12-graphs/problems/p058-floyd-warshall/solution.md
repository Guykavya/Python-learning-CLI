## Approach

Dynamic programming over the set of allowed middle vertices. With the middle vertices `0 .. k-1` allowed, the best route from `i` to `j` that may also use `k` either avoids `k` (the old value) or goes `i ~> k ~> j` (two old values). One table updated in place is enough, because in round `k` the entries of row `k` and column `k` do not change.

## Code

```python
def floyd_warshall(n, edges):
    INF = float("inf")
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        if w < dist[u][v]:
            dist[u][v] = w
    for k in range(n):
        dk = dist[k]
        for i in range(n):
            dik = dist[i][k]
            if dik == INF:
                continue
            di = dist[i]
            for j in range(n):
                if dik + dk[j] < di[j]:
                    di[j] = dik + dk[j]
    return dist
```

The local names `dk`, `di` and the skip of an infinite `dist[i][k]` only make it faster; the logic is the three loops.

## Complexity

`O(V^3)` time, `O(V^2)` memory. For 150 vertices that is about 3.4 million steps.

## Another way

Run Dijkstra from every vertex (non-negative weights only): `O(V (V + E) log V)`, faster on sparse graphs. Run Bellman-Ford from every vertex for negative weights: `O(V^2 E)`, slower. Johnson's algorithm re-weights the edges once with Bellman-Ford and then runs Dijkstra from every vertex. A negative cycle shows up after Floyd-Warshall as `dist[i][i] < 0`.
