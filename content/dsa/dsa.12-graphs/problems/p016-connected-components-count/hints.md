## Hint 1

One search from `s` visits exactly the component of `s`. If you start a new search from every vertex that no earlier search has reached, how many searches do you start?

Is `n - len(edges)` the answer? Try it on the triangle of the third example.

## Hint 2

```
seen = [False] * n; count = 0
for s in range(n):
    if seen[s]: continue
    count += 1; seen[s] = True; stack = [s]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if not seen[v]: seen[v] = True; stack.append(v)
return count
```
