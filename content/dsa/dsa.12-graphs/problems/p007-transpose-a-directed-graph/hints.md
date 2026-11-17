## Hint 1

`transpose` is p001 again, with the edges turned around. Where does the edge `u -> v` go in the new lists? Loop over `u` and over `adj[u]` in order, and the required order comes by itself.

## Hint 2

```
transpose: rev = [[] for _ in adj]; for u, nbrs in enumerate(adj): for v in nbrs: rev[v].append(u)
can_reach: rev = transpose(adj)
           seen = {target}; queue = deque([target])
           while queue: u = popleft; for v in rev[u]: if v not in seen: add, append
           return sorted(seen)
```

Why is a forward search from every vertex (does `u` reach `target`?) too slow?
