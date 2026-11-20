## Hint 1

Which vertices may come first? Once you have placed a vertex, which edges stop mattering, and how does that change which vertices may come next? What does the in-degree of a vertex count?

## Hint 2

Build `adj` (out-edges) and `indeg` from the edge list, one count per listed edge. Fill a `deque` with all vertices of in-degree 0. Pop from the left, append to `order`, and for each out-neighbour `v` do `indeg[v] -= 1`; push `v` when it reaches 0. At the end compare `len(order)` with `n`.

## Hint 3

```
adj = [[] for _ in range(n)]; indeg = [0] * n
for u, v in edges: adj[u].append(v); indeg[v] += 1
ready = deque(v for v in range(n) if indeg[v] == 0)
order = []
while ready:
    u = ready.popleft(); order.append(u)
    for v in adj[u]:
        indeg[v] -= 1
        if indeg[v] == 0: ready.append(v)
return order if len(order) == n else []
```
