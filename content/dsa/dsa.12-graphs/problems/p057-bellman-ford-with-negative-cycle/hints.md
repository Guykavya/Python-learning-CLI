## Hint 1

A shortest route without a repeated vertex has at most `V - 1` edges. After round `k`, all vertices whose best route has at most `k` edges are correct. So after `V - 1` rounds, every distance that exists is final. What does it mean if a round after that still changes something?

## Hint 2

Only relax an edge when `dist[u]` is finite (`dist[u] != inf`). Then a cycle that is not reachable keeps its vertices at `inf` and cannot "improve" in the extra round. A cycle that **is** reachable and negative keeps getting cheaper every round, so the extra round finds an edge with `dist[u] + w < dist[v]`.

## Hint 3

```
dist = [inf] * n;  dist[source] = 0
repeat n - 1 times:
    for u, v, w in edges:
        if dist[u] != inf and dist[u] + w < dist[v]: dist[v] = dist[u] + w
for u, v, w in edges:                      # the extra round
    if dist[u] != inf and dist[u] + w < dist[v]: return None
return dist
```
