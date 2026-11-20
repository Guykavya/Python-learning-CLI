## Approach

The chapter's `dfs_recursive`: mark and record `u`, then recurse into each unvisited neighbour in adjacency order. The `if v not in visited` check is done right before the call, so a vertex that was visited deeper in an earlier branch is skipped.

## Code

```python
def dfs_order(n, edges, start):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        if u != v:
            adj[v].append(u)
    visited, order = set(), []

    def visit(u):
        visited.add(u)
        order.append(u)
        for v in adj[u]:
            if v not in visited:
                visit(v)

    visit(start)
    return order
```

## Complexity

`O(n + E)` time; the recursion depth can reach `n`, which is why p013 replaces it with a stack.

## Another way

Problem p013: an explicit stack, pushing neighbours in reverse and skipping already-visited vertices when popped, gives exactly this order without recursion.
