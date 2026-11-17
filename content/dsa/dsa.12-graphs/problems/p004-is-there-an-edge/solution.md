## Approach

Keep two views of the same edges: a list per vertex for the order, and a set per vertex for membership tests. Both together are still `O(n + E)` memory (each edge end is stored twice instead of once).

## Code

```python
class EdgeIndex:
    def __init__(self, n, edges, directed=False):
        self.adj = [[] for _ in range(n)]
        self.nbr = [set() for _ in range(n)]
        for u, v in edges:
            self.adj[u].append(v)
            self.nbr[u].add(v)
            if not directed and u != v:
                self.adj[v].append(u)
                self.nbr[v].add(u)

    def neighbours(self, u):
        return list(self.adj[u])

    def has_edge(self, u, v):
        return v in self.nbr[u]
```

## Complexity

Building: `O(n + E)`. `neighbours(u)`: `O(degree(u))` (it copies the list). `has_edge`: `O(1)` on average.

| structure | memory | `has_edge` | neighbours |
|---|---|---|---|
| list of lists | `O(n + E)` | `O(degree)` | `O(degree)` |
| matrix | `O(n^2)` | `O(1)` | `O(n)` |
| list of sets (+ lists) | `O(n + E)` | `O(1)` average | `O(degree)` |

## Another way

A single set of pairs, `edges = {(u, v), ...}` (and `(v, u)` for undirected graphs), also answers `has_edge` in `O(1)`; it is what some solutions use when they never need neighbour lists. If the order of neighbours did not matter, the sets alone would be enough.
