## Hint 1

This is Dijkstra from `k`, followed by one more question. Which question? "When does the **last** server get the signal?" Is that the sum of the distances, or something else?

## Hint 2

Make the distance table for **all** servers `1 .. n` (a list of length `n + 1` and ignore index 0, or a dictionary built from `range(1, n + 1)`). A server that appears in no link must still count. After Dijkstra, if any of those distances is still infinite, return `-1`.

## Hint 3

```
adj = [[] for _ in range(n + 1)]
for u, v, t in times: adj[u].append((v, t))
dist = dijkstra over adj from k          # dist[0] is unused
worst = max(dist[1:])
return -1 if worst == inf else worst
```
