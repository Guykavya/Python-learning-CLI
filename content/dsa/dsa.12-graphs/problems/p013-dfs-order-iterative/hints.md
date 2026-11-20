## Hint 1

A stack gives back the **last** thing pushed. If you push `adj[u]` in order, which neighbour comes out first? Now trace the second example with "mark when pushed": after popping `0` you push `1` and `2` and mark both. Can `2` still be reached through `1`, as recursion does?

## Hint 2

```
visited = set(); order = []; stack = [start]
while stack:
    u = stack.pop()
    if u in visited: continue          # an old copy: skip it
    visited.add(u); order.append(u)
    for v in reversed(adj[u]):
        if v not in visited: stack.append(v)
return order
```

The stack can hold up to `O(E)` entries, because a vertex can be pushed once per edge.
