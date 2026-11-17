## Approach

The cut "tree so far" against "everything else": its cheapest crossing edge belongs to a minimum spanning tree (the cut property). The heap holds candidate crossing edges; some become stale when their far end joins the tree by another edge, and they are skipped when they come out, exactly like the stale entries of Dijkstra.

## Code

```python
import heapq


def prim(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((w, u, v))
        adj[v].append((w, v, u))
    in_tree = [False] * n
    in_tree[0] = True
    heap = list(adj[0])
    heapq.heapify(heap)
    tree, total = [], 0
    while heap and len(tree) < n - 1:
        w, u, v = heapq.heappop(heap)
        if in_tree[v]:
            continue
        in_tree[v] = True
        tree.append((u, v, w))
        total += w
        for item in adj[v]:
            if not in_tree[item[2]]:
                heapq.heappush(heap, item)
    if len(tree) < n - 1:
        return None
    return total, tree
```

## Complexity

Every edge is pushed at most twice (once from each end): `O(E log E) = O(E log V)` time, `O(V + E)` memory.

## Another way

Kruskal (previous problem) sorts all edges and joins groups with Union-Find; it gives the same total but adds the edges in a different order. For dense graphs, Prim without a heap (`best[v]` = cheapest edge from the tree to `v`, pick the smallest by scanning) is `O(V^2)`, which the next problem uses.
