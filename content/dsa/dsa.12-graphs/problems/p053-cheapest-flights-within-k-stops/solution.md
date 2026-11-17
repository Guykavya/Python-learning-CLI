## Approach

Round `i` of Bellman-Ford makes every price that needs at most `i` flights correct, **if** a round extends each route by one flight only. Reading from a copy of the previous round guarantees that. After `k + 1` rounds, `dist[dst]` is the cheapest route with at most `k + 1` flights, that is at most `k` stops.

## Code

```python
def find_cheapest_price(n, flights, src, dst, k):
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):
        prev = dist[:]
        for u, v, price in flights:
            if prev[u] + price < dist[v]:
                dist[v] = prev[u] + price
    return -1 if dist[dst] == INF else dist[dst]
```

## Complexity

`O(k * E)` time and `O(n)` memory.

## Another way

**Dijkstra on states** `(city, flights used)`: the vertex is the pair, an edge adds one flight, and states that already used `k + 1` flights are not expanded. Whatever limits the future must be part of the state (chapter section 18). Stop when `dst` is popped. In the worst case there are `n * (k + 2)` states, so it costs more memory, but it is often fast. Plain Dijkstra on cities alone is wrong: it keeps only the cheapest route to each city and throws away a more expensive one with fewer flights, which may be the only one that fits the limit.
