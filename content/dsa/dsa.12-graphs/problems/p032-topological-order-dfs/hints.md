## Hint 1

When does DFS finish a vertex `u`? Everything reachable from `u` is finished before `u` is. So in the finishing list every vertex appears **after** all vertices that must come after it. What do you do with that list?

## Hint 2

Keep `colour` per vertex. For each WHITE start vertex: colour it GREY and push `(s, iter(adj[s]))`. Loop: look at the top `(u, it)` and take `v = next(it, None)`. If `v is None`, `u` is finished: colour BLACK, append to `finished`, pop. If `v` is GREY, there is a cycle: return `[]`. If `v` is WHITE, colour it GREY and push it. At the end return `finished[::-1]`.

## Hint 3

```
for s in range(n):
    if colour[s] != WHITE: continue
    colour[s] = GREY; stack = [(s, iter(adj[s]))]
    while stack:
        u, it = stack[-1]
        v = next(it, None)
        if v is None:   colour[u] = BLACK; finished.append(u); stack.pop()
        elif colour[v] == GREY:  return []
        elif colour[v] == WHITE: colour[v] = GREY; stack.append((v, iter(adj[v])))
return finished[::-1]
```
