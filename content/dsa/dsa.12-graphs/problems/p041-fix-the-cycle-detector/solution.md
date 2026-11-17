## What is wrong

The starter treats **any** visited module as a cycle. In a directed graph a module can be reached twice without any circle: in the complaint `util` is reached from `db` and again from `web`. When the DFS meets it the second time, `util` is already finished, and nothing reachable from it leads back. The rule "seen = cycle" is the undirected rule, used on a directed graph (chapter section 6 shows exactly this mistake on a diamond).

A directed cycle shows up as an edge to a module that is **on the current path**: the DFS walked from `v` down to `u`, and now `u` points back to `v`. So we must remember three states, not two.

## The fix

```python
WHITE, GREY, BLACK = 0, 1, 2


def has_cycle(graph):
    """True if the import graph has a directed cycle."""
    colour = {u: WHITE for u in graph}

    def visit(u):
        colour[u] = GREY                       # on the current path
        for v in graph[u]:
            if colour[v] == GREY:
                return True                    # back to the current path: a cycle
            if colour[v] == WHITE and visit(v):
                return True
        colour[u] = BLACK                      # finished: safe for ever
        return False

    return any(colour[u] == WHITE and visit(u) for u in graph)
```

The BLACK state does two jobs. It tells the DFS that meeting a finished module is harmless, and it makes sure no module is explored twice. A tempting half-fix keeps only the current path (add when entering, remove when leaving). It answers correctly, but a finished module becomes "unvisited" again, so it is explored once for every path that reaches it. The layered test has `4**39`, more than `10**23`, paths, so that version never ends.

## Complexity

Every module is entered once (WHITE -> GREY -> BLACK) and every import edge is followed once: `O(V + E)`. The recursion is as deep as the longest import chain.

## Another way

Kahn's algorithm (chapter section 7): count how many edges point **into** each module, repeatedly remove modules with in-degree 0, and report a cycle if some module is never removed. It needs no recursion and no colours.
