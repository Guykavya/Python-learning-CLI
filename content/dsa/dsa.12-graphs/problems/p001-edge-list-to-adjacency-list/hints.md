## Hint 1

Start with one empty list per vertex. How do you make `n` **different** empty lists? Try `a = [[]] * 3; a[0].append(5); print(a)` and look at what happens.

## Hint 2

```
adj = [[] for _ in range(n)]
for u, v in edges:
    adj[u].append(v)
    if not directed and u != v:      # a self loop only once
        adj[v].append(u)
return adj
```
