## Hint 1

What does a queue give you that a stack does not? The vertex that waited **longest** comes out first, so all vertices at distance 1 come out before any vertex at distance 2. What must you remember for each vertex so that it enters the queue only once?

## Hint 2

```
build adj in edge-list order
seen = {start}; queue = deque([start]); order = []
while queue:
    u = queue.popleft(); order.append(u)
    for v in adj[u]:
        if v not in seen: seen.add(v); queue.append(v)
return order
```
