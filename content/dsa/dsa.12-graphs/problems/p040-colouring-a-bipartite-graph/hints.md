## Hint 1

Put person `s` in group 0. Where must everyone they dislike go? And everyone **those** people dislike? Is anything left to choose inside one connected piece of the dislike graph?

## Hint 2

Build an undirected adjacency list. `group = [-1] * n`. For every person still at `-1`: put them in group 0 and BFS; each uncoloured neighbour gets `1 - group[u]`; a neighbour already in the **same** group as `u` means return `None`. People who are alone get group 0 from the outer loop.

## Hint 3

```
group = [-1] * n
for s in range(n):
    if group[s] != -1: continue
    group[s] = 0; queue = deque([s])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if group[v] == -1: group[v] = 1 - group[u]; queue.append(v)
            elif group[v] == group[u]: return None
return group
```
