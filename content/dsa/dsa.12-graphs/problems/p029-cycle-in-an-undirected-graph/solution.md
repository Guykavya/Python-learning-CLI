## Approach

A search reaches every vertex through one edge. In an undirected graph, if a vertex `v` can be reached a second time through a **different** edge, the two routes to `v` close a cycle. So the rule is: a seen neighbour means a cycle, except for the one edge we arrived by.

We keep `(vertex, parent)` pairs on a stack (no recursion, so long paths are fine). We mark a vertex as seen when we push it. Looking at the neighbours of `u`, we skip the parent; any other neighbour that is already seen proves a cycle.

Two special cases come out right without extra code. **Parallel edges**: `0 - 1` listed twice is a real cycle of length 2. In `1`'s list both copies of `0` are skipped, but `0` handles its own list first: the first copy of `1` is pushed and marked, the second copy finds `1` already seen, so the cycle is reported there. **Self loops**: `(u, u)` puts `u` in its own list; `u` is seen and is not its own parent, so it counts as a cycle.

```python
def has_cycle(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, -1)]
        while stack:
            u, parent = stack.pop()
            for v in adj[u]:
                if v == parent:
                    continue                       # the edge we arrived by
                if seen[v]:
                    return True                    # a second way to reach v
                seen[v] = True
                stack.append((v, u))
    return False
```

## Complexity

Every vertex is pushed once and every edge is looked at twice: `O(n + E)`.

## Another way

Union-Find (chapter section 9): for each edge `(u, v)`, if `u` and `v` are already in the same group, this edge closes a cycle; otherwise unite them. A self loop finds `u` and `u` in the same group at once. Or count: a graph without cycles is a forest, and a forest with `C` pieces has exactly `n - C` edges, so there is a cycle exactly when `len(edges) > n - C`.
