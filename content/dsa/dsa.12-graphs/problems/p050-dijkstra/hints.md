## Hint 1

Build an adjacency list first: `adj = [[] for _ in range(n)]`, and for each edge `adj[u].append((v, w))`. Then keep `dist = [inf] * n` with `dist[source] = 0`. What should the heap hold at the start?

## Hint 2

The heap holds pairs `(d, u)`: "I know a route of length `d` to `u`". When you pop one, it may be **old**: a better route to `u` was found after it was pushed. How do you recognise that with one comparison against `dist[u]`?

## Hint 3

```
dist = [inf] * n;  dist[source] = 0
heap = [(0, source)]
while heap:
    d, u = heappop(heap)
    if d > dist[u]: continue            # stale entry
    for v, w in adj[u]:
        if d + w < dist[v]:
            dist[v] = d + w
            heappush(heap, (d + w, v))
return dist
```
