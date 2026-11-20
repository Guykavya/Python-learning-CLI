## Approach

Create one empty list per vertex with a comprehension, then walk the edge list once. Each edge adds one entry (directed) or two entries (undirected), except a self loop, which adds one.

## Code

```python
def build_adj(n, edges, directed=False):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        if not directed and u != v:
            adj[v].append(u)
    return adj
```

## Complexity

`O(n + E)` time and memory: `n` lists and at most `2E` entries.

## Another way

With named vertices, use a dictionary: `adj = {v: [] for v in names}` (create the keys for **all** vertices first, so isolated ones exist), or `collections.defaultdict(list)` when the vertices are only known from the edges. If you will often ask "is `v` a neighbour of `u`?", store sets instead of lists (`O(1)` membership), but then the order is lost.
