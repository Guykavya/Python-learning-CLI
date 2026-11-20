## Hint 1

A dictionary per vertex gives `O(1)` "do I already have an edge to `v`?". When you add `(u, v, w)`, what should happen if `v` is already a key of `adj[u]`?

## Hint 2

```
adj = [{} for _ in range(n)]
def put(a, b, w):
    if b not in adj[a] or w < adj[a][b]:
        adj[a][b] = w
for u, v, w in edges:
    put(u, v, w)
    if not directed: put(v, u, w)
```
