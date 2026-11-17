## Hint 1

You never need to know **who** the neighbours are, only how many edge ends touch each vertex. Can you count while you read the edges once, with a list of counters?

## Hint 2

```
undirected:  deg = [0] * n;  for u, v in edges: deg[u] += 1; deg[v] += 1
directed:    indeg, outdeg = [0] * n, [0] * n
             for u, v in edges: outdeg[u] += 1; indeg[v] += 1
```

Check the self loop by hand: `(0, 0)` runs `deg[0] += 1` twice. Is that what the statement wants?
