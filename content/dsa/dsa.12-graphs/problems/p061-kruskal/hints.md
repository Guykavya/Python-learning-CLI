## Hint 1

You need a fast answer to "are `u` and `v` already in the same group?" while groups keep merging. Which structure from section 9 does that in almost `O(1)`? When you take an edge, what do you do with the two groups?

## Hint 2

Sort with `sorted(edges, key=lambda e: e[2])`. Keep a counter of the edges you took. A tree on `n` vertices has exactly `n - 1` edges: if you took fewer after looking at every edge, the graph is not connected.

## Hint 3

```
parent = list(range(n))          # DSU with find (path halving) and union
total = taken = 0
for u, v, w in sorted(edges, key=weight):
    if find(u) != find(v):
        union(u, v);  total += w;  taken += 1
        if taken == n - 1: break
return total if taken == n - 1 else None
```
