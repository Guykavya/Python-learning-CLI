## Approach

Loop over **all** vertices; every unseen vertex starts a new search (BFS or an iterative DFS), which marks its whole component. The number of searches is the number of components.

## Code

```python
def count_components(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    count = 0
    for s in range(n):
        if seen[s]:
            continue
        count += 1
        seen[s] = True
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
    return count
```

## Complexity

`O(n + E)`: all the searches together visit every vertex once and every edge twice.

## Another way

Union-Find (section 9): start with `n` groups and do `union(u, v)` for every edge; each union that joins two different groups lowers the count by one. `n - len(edges)` is right only for a **forest** (no cycles, no parallel edges, no self loops).
