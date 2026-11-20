## Hint 1

A list keeps the order but is slow for "is `v` in it?". Which Python container answers "is `v` in it?" in `O(1)`? Can you keep **both** a list and that container for every vertex? What does that cost in memory?

## Hint 2

```
__init__:  self.adj = [[] for _ in range(n)]       # order, for neighbours()
           self.nbr = [set() for _ in range(n)]    # membership, for has_edge()
           for u, v in edges: add v to adj[u] and to nbr[u]; if undirected and u != v: the same for v
neighbours(u): return list(self.adj[u])
has_edge(u, v): return v in self.nbr[u]
```
