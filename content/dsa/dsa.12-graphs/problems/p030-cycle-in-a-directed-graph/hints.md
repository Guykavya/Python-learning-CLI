## Hint 1

A directed cycle exists exactly when the DFS finds an edge `u -> v` while `v` is still "open" (entered but not finished). How can you tell "open" from "finished"? Why are two states (seen / not seen) not enough?

## Hint 2

Keep `colour[v]` in `{WHITE, GREY, BLACK}`. For a recursive version: colour `u` GREY, visit every neighbour (GREY neighbour = cycle; WHITE neighbour = visit it), then colour `u` BLACK. To avoid recursion, put pairs `(u, iterator over adj[u])` on a stack: look at the top, take the next neighbour; when the iterator is exhausted, colour `u` BLACK and pop it.

## Hint 3

```
for s in range(n):
    if colour[s] != WHITE: continue
    colour[s] = GREY; stack = [(s, iter(adj[s]))]
    while stack:
        u, it = stack[-1]
        v = next(it, None)
        if v is None: colour[u] = BLACK; stack.pop()
        elif colour[v] == GREY: return True
        elif colour[v] == WHITE: colour[v] = GREY; stack.append((v, iter(adj[v])))
return False
```
