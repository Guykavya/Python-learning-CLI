## Hint 1

Start the table from the edges alone: 0 on the diagonal, the cheapest direct edge `i -> j` elsewhere, `inf` if there is none. Then, for one middle vertex `k`, which single comparison improves `dist[i][j]`?

## Hint 2

After processing the middle vertices `0 .. k`, `dist[i][j]` is the best route whose middle vertices all come from `0 .. k`. For that to work, the entries `dist[i][k]` and `dist[k][j]` must already be final for the earlier middle vertices when you use them, so `k` must change **slowest**: it is the outer loop.

## Hint 3

```
dist = [[0 if i == j else inf for j in range(n)] for i in range(n)]
for u, v, w in edges: dist[u][v] = min(dist[u][v], w)
for k in range(n):
    for i in range(n):
        for j in range(n):
            if dist[i][k] + dist[k][j] < dist[i][j]:
                dist[i][j] = dist[i][k] + dist[k][j]
return dist
```
