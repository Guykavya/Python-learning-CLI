## Hint 1

In the complaint, the DFS goes `app -> db -> util`, comes back, then goes `app -> web -> util`. `util` is visited, so the starter says "cycle". But `util` was **finished**: nothing from `util` leads back to `web` or `app`. Only a module that is still **open** (on the current path) can close a circle.

## Hint 2

Use three colours (chapter section 6): WHITE = not visited, GREY = entered and not finished (on the current path), BLACK = finished. An edge to a GREY module is a cycle. An edge to a BLACK module is harmless and must not be explored again. An edge to a WHITE module is explored.

## Hint 3

```
colour = {u: WHITE for u in graph}
def visit(u):
    colour[u] = GREY
    for v in graph[u]:
        if colour[v] == GREY: return True
        if colour[v] == WHITE and visit(v): return True
    colour[u] = BLACK
    return False
return any(colour[u] == WHITE and visit(u) for u in graph)
```

Why BLACK and not simply "remove `u` from the path when leaving"? Without BLACK, a finished module is explored again from every path that reaches it: on the layered project that is more than `10**23` times.
