## Approach

Turning every edge around takes one pass. A vertex `u` can reach `target` exactly when there is a path `u -> ... -> target`; in the transpose the same edges point the other way, so it is a path `target -> ... -> u`. One BFS from `target` in the transpose finds all such `u` at once.

## Code

```python
from collections import deque


def transpose(adj):
    rev = [[] for _ in adj]
    for u, nbrs in enumerate(adj):
        for v in nbrs:
            rev[v].append(u)
    return rev


def can_reach(adj, target):
    rev = transpose(adj)
    seen = {target}
    queue = deque([target])
    while queue:
        u = queue.popleft()
        for v in rev[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return sorted(seen)
```

## Complexity

`transpose`: `O(n + E)`. `can_reach`: `O(n + E)` for the transpose and the BFS, plus `O(k log k)` to sort the `k` vertices found. Asking "does `u` reach `target`?" with one forward search per vertex would be `O(n (n + E))`.

## Another way

For an undirected graph the transpose is the graph itself, and `can_reach` is just the component of `target`. If many targets are asked, compute the strongly connected components once and work on the condensation (section 16).
