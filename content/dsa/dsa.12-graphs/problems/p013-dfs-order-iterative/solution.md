## Approach

Replace the call stack by a list. Mark on **pop**: the copy of a vertex pushed most recently is the one recursion would enter next, and older copies are skipped when they come out. Push neighbours **reversed**, so that the first neighbour ends on top.

## Code

```python
def dfs_order(n, edges, start):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        if u != v:
            adj[v].append(u)
    visited, order = set(), []
    stack = [start]
    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        order.append(u)
        for v in reversed(adj[u]):
            if v not in visited:
                stack.append(v)
    return order
```

## Complexity

`O(n + E)` time; the stack holds at most `O(E)` entries.

## Another way

Keep an **iterator** per vertex on the stack (chapter `dfs_enter_exit`): look at the top vertex, take its next neighbour, and push that neighbour only if it is unvisited; pop the vertex when its iterator is used up. This mimics the recursion exactly, keeps the stack at `O(n)`, and also tells you when each vertex is **finished**, which topological sort and SCC need.

```python
def dfs_order(n, edges, start):
    adj = ...                                    # as above
    visited, order = {start}, [start]
    stack = [iter(adj[start])]
    while stack:
        v = next(stack[-1], None)
        if v is None:
            stack.pop()
        elif v not in visited:
            visited.add(v)
            order.append(v)
            stack.append(iter(adj[v]))
    return order
```
