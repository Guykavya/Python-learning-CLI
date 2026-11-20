## Hint 1

A DFS also finds **a** path, but is it the shortest? (Chapter "Try it 2": DFS finds `0 1 2 3` on a ring where `0 3` is one edge.) Which search reaches vertices in order of their distance?

## Hint 2

```
dist = {s: 0}; queue = deque([s])
while queue:
    u = popleft
    if u == t: return dist[u]
    for v in adj[u]:
        if v not in dist: dist[v] = dist[u] + 1; append v
return -1
```
