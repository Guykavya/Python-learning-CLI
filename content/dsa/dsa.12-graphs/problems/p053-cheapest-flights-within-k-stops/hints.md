## Hint 1

After round 1 of Bellman-Ford, which cities have a correct "cheapest with at most 1 flight" price? After round 2? So how many rounds do you need for at most `k + 1` flights?

## Hint 2

Inside one round, if you write into the same list you read from, a price set early in the round can be used again later in the **same** round: one round may then add two or three flights. Read from `prev = dist[:]` (the prices after the previous round) and write into `dist`.

## Hint 3

```
dist = [inf] * n;  dist[src] = 0
repeat k + 1 times:
    prev = dist[:]
    for u, v, p in flights:
        if prev[u] + p < dist[v]: dist[v] = prev[u] + p
return -1 if dist[dst] is inf else dist[dst]
```
