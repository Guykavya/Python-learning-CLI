## Hint 1

Build the adjacency list. Then a BFS from node 0, without recursion: a list `order` that you extend while you walk through it, and a list `parent` (`parent[0] = -1`). Every node appears in `order` after its parent.

## Hint 2

Start every node with `take[v] = 1` and `skip[v] = 0`. Walk `order` **backwards**: when you reach `v`, all its children were processed already (they come later in BFS order), so `take[v]` and `skip[v]` are final. Then push them into the parent:
`take[p] += skip[v]` and `skip[p] += max(take[v], skip[v])`.

## Hint 3

```
adj = adjacency lists
parent = [-1] * n; seen = [False] * n; seen[0] = True
order = [0]; i = 0
while i < len(order):
    v = order[i]; i += 1
    for w in adj[v]:
        if not seen[w]: seen[w] = True; parent[w] = v; order.append(w)
take = [1] * n; skip = [0] * n
for v in reversed(order):
    p = parent[v]
    if p != -1:
        take[p] += skip[v]; skip[p] += max(take[v], skip[v])
return max(take[0], skip[0])
```
