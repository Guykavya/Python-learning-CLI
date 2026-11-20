## Hint 1

Start with `in_tree = {0}` and push every edge of 0 as `(w, 0, v)`. Pop the cheapest. If `v` is already in the tree, the edge is stale: skip it. Otherwise add `v`, record the edge, and push the edges of `v` that lead out of the tree. What is the key: `w`, or the distance from 0 plus `w`?

## Hint 2

The key is the **single edge weight** `w`. (Dijkstra pushes `dist[u] + w`; Prim does not care how far `u` is from vertex 0.) Build an adjacency list where each undirected edge appears in both lists. Stop when the tree has `n` vertices; if the heap runs empty first, the graph is not connected.

## Hint 3

```
adj[u] gets (w, u, v) and adj[v] gets (w, v, u) for every edge
in_tree = [False] * n;  in_tree[0] = True
heap = adj[0][:];  heapify(heap);  tree = [];  total = 0
while heap and len(tree) < n - 1:
    w, u, v = heappop(heap)
    if in_tree[v]: continue
    in_tree[v] = True;  tree.append((u, v, w));  total += w
    for item in adj[v]:
        if not in_tree[item[2]]: heappush(heap, item)
return (total, tree) if len(tree) == n - 1 else None
```
