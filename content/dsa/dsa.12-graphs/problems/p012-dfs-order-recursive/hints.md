## Hint 1

Write a helper `visit(u)` inside `dfs_order` that can see `adj`, `visited` and `order`. What three things does `visit(u)` do, and in which order? When does the recursion stop?

## Hint 2

```
visited = set(); order = []
def visit(u):
    visited.add(u); order.append(u)
    for v in adj[u]:
        if v not in visited: visit(v)
visit(start)
return order
```
