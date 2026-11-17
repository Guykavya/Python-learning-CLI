## Hint 1

BFS from `s` reaches every vertex for the first time along a shortest path. At that moment, which vertex "brought" it? If every vertex remembers that one vertex, how do you get from `t` back to `s`?

## Hint 2

```
parent = {s: None}; queue = deque([s])
while queue:
    u = popleft
    if u == t: break
    for v in adj[u]:
        if v not in parent: parent[v] = u; append v
if t not in parent: return None
path = []; x = t
while x is not None: path.append(x); x = parent[x]
return path reversed
```

Why is a recursive "walk back" a bad idea on a path of 100,000 vertices?
