## Hint 1

If vertex `u` has colour 0, which colour must every neighbour of `u` have? Once the start vertex of a piece has a colour, is anything left to choose?

## Hint 2

`colour = [-1] * n`. For every vertex `s` with colour `-1`: set it to 0 and BFS. When you pop `u`, look at each neighbour `v`: if `v` has no colour, give it `1 - colour[u]` and push it; if it has the **same** colour as `u`, return `False`. After all pieces, return `True`.

## Hint 3

```
for s in range(n):
    if colour[s] != -1: continue
    colour[s] = 0; queue = deque([s])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if colour[v] == -1: colour[v] = 1 - colour[u]; queue.append(v)
            elif colour[v] == colour[u]: return False
return True
```
