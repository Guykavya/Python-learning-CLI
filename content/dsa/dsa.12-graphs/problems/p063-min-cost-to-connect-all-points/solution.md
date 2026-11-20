## Approach

The graph is complete, so it is dense: `E` is about `V^2 / 2`. Prim with an array is `O(V^2)`, which is exactly the size of the input graph, and needs only `O(V)` memory because edge weights are computed on the fly. Each step joins the point that is cheapest to join to the whole tree (not only to the last point), which is the cut property again.

## Code

```python
def min_cost_connect_points(points):
    n = len(points)
    INF = float("inf")
    best = [INF] * n
    best[0] = 0
    in_tree = [False] * n
    total = 0
    for _ in range(n):
        u = -1
        for i in range(n):
            if not in_tree[i] and (u == -1 or best[i] < best[u]):
                u = i
        in_tree[u] = True
        total += best[u]
        ux, uy = points[u]
        for v in range(n):
            if not in_tree[v]:
                cost = abs(ux - points[v][0]) + abs(uy - points[v][1])
                if cost < best[v]:
                    best[v] = cost
    return total
```

## Complexity

`O(n^2)` time (about a million steps for `n = 1000`), `O(n)` memory.

## Another way

Kruskal on all `n (n - 1) / 2` pairs: build the list, sort it (`O(n^2 log n)`) and use Union-Find. It is correct but stores half a million tuples for `n = 1000`. Heap-based Prim pushes up to `n^2` entries as well. For Manhattan distances there is also an `O(n log n)` trick (only 4 "nearest in each octant" neighbours per point can be MST edges), well beyond this module.
