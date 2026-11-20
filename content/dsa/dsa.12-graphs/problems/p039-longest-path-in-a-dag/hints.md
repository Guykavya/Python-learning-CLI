## Hint 1

When can you be sure that `best[v]` will not change any more? Only when every edge **into** `v` has been looked at. Which order of the vertices guarantees that for all of them at once?

## Hint 2

Get a topological order with Kahn (p031). Then go through the vertices in that order and **push** values forward along the out-edges: for an edge `u -> v` with weight `w`, if `best[u]` is not `None`, set `best[v] = max(best[v], best[u] + w)` (treating `None` as "no path yet"). For counting: `ways[v] = (ways[v] + ways[u]) % MOD`.

## Hint 3

```
order = kahn(n, edges)
best = [None] * n; best[source] = 0
for u in order:
    if best[u] is None: continue
    for v, w in adj[u]:
        if best[v] is None or best[u] + w > best[v]: best[v] = best[u] + w

ways = [0] * n; ways[source] = 1
for u in order:
    for v, w in adj[u]: ways[v] = (ways[v] + ways[u]) % MOD
return ways[target]
```
