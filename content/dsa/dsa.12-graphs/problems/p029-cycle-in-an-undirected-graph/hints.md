## Hint 1

During a search, every vertex is reached by exactly one edge, its "tree edge". If you meet a vertex that is already seen through a **different** edge, there are two ways to reach it: that is a cycle. How do you recognise the tree edge of `u` when you look at `u`'s neighbours?

## Hint 2

Push pairs `(vertex, parent)` on a stack and mark a vertex as seen when you push it. When you look at the neighbours of `u`, skip the parent; a neighbour that is already seen is a cycle; otherwise mark it and push it. Start a new search from every unseen vertex. Parallel edges need no extra code: when the parent `p` handles its own list, the second copy of `u` is already seen.

## Hint 3

```
for s in range(n):
    if seen[s]: continue
    seen[s] = True; stack = [(s, -1)]
    while stack:
        u, parent = stack.pop()
        for v in adj[u]:
            if v == parent: continue
            if seen[v]: return True
            seen[v] = True; stack.append((v, u))
return False
```
