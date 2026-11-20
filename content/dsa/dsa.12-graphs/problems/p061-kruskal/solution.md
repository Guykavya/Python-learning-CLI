## Approach

The cut property: for any split of the vertices into two sides, the cheapest edge across the split belongs to some minimum spanning tree. When Kruskal looks at an edge whose ends are in different groups, it is the cheapest edge leaving either group (all cheaper edges were already looked at), so taking it is safe. An edge inside one group would close a cycle and is skipped. Union-Find keeps the groups.

## Code

```python
def kruskal(n, edges):
    parent = list(range(n))
    size = [1] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]      # path halving
            x = parent[x]
        return x

    total, taken = 0, 0
    if n == 1:
        return 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru == rv:
            continue
        if size[ru] < size[rv]:
            ru, rv = rv, ru
        parent[rv] = ru
        size[ru] += size[rv]
        total += w
        taken += 1
        if taken == n - 1:
            return total
    return None
```

## Complexity

Sorting dominates: `O(E log E)`; the Union-Find work is almost `O(E)`. Memory `O(V + E)` for the sorted copy.

## Another way

Prim's algorithm grows one tree from a start vertex with a heap of edges leaving the tree: `O(E log V)`, and for dense graphs `O(V^2)` without a heap (next problems). Both give the same total; if all weights are different, even the same tree.
