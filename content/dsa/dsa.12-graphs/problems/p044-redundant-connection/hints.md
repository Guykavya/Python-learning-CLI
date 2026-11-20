## Hint 1

Add the edges one by one. As long as no cycle has formed, the edges added so far form a forest. When does adding `(u, v)` close a cycle? How can you check that quickly, without searching the graph each time?

## Hint 2

Use a DSU. For each edge `(u, v)` in order: if `find(u) == find(v)`, return this edge; otherwise unite them. Before the edge that closes the cycle, all the other edges of the cycle were already added, so this one is the cycle's last edge in the list.

## Hint 3

```
parent = list(range(n))
def find(x): ... (loop with path compression)
for u, v in edges:
    ru, rv = find(u), find(v)
    if ru == rv: return (u, v)
    parent[ru] = rv
```
