## Hint 1

Store one adjacency list per vertex of pairs `(v, w)`. Every method then walks `self.adj`. Do the checks in `add_edge` first (range, negative weight), then append. Which methods are "BFS with a queue", which are "DFS with a stack", and which need a heap?

## Hint 2

`dfs` without recursion, in the recursive order:

```
seen = [False] * n;  order = [];  stack = [s]
while stack:
    u = stack.pop()
    if seen[u]: continue
    seen[u] = True;  order.append(u)
    for v, _ in reversed(adj[u]): if not seen[v]: stack.append(v)
```

`components` runs a search from every unseen vertex in increasing order; each search collects one component (sort it). `topo` is Kahn's algorithm: count in-degrees, start with all vertices of in-degree 0, and if fewer than `n` vertices come out there is a cycle.

## Hint 3

`shortest` is the lazy Dijkstra of section 10 (`dist`, a heap of `(d, u)`, skip `d > dist[u]`). Write the class in small steps and test each method on the example before the next one. For the `ValueError` checks: `if self.directed: raise ValueError("components() needs an undirected graph")`.
