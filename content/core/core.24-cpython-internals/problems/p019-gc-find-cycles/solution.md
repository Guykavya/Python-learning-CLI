## Approach

Breadth-first search over the referent graph, starting from `obj`. The frontier holds all
objects exactly `k` steps away; each round expands it by one step. The first time we meet `obj`
again, the path is the shortest one, and the `parent` links (keyed by `id`, since lists and dicts
are unhashable) give it back in reverse.

Three details make it correct and fast:

- `ref is obj` is checked **before** the "seen" test, so the start object is recognised as the
  goal and never queued again.
- Classes, modules and functions are never expanded. They connect almost everything in the
  program, so walking them is slow and reports false cycles through globals (`KEEP`).
- `seen` stores the objects, not just their ids: a freed object's id can be reused, which would
  make the search skip an unrelated new object.

## Code

```python
import gc
import types


def _followable(x):
    return not isinstance(x, (type, types.ModuleType, types.FunctionType))


def cycle_path(obj, max_depth=100):
    parent = {}
    seen = {}
    frontier = [obj]
    for step in range(max_depth):
        next_frontier = []
        for node in frontier:
            for ref in gc.get_referents(node):
                if ref is obj:
                    path = [obj]
                    current = node
                    while current is not obj:
                        path.append(current)
                        current = parent[id(current)]
                    path.append(obj)
                    path.reverse()
                    return path
                if id(ref) in seen or not _followable(ref):
                    continue
                seen[id(ref)] = ref
                parent[id(ref)] = node
                next_frontier.append(ref)
        frontier = next_frontier
        if not frontier:
            break
    return None


def in_cycle(obj, max_depth=100):
    return cycle_path(obj, max_depth) is not None
```

## Complexity

O(V + E) for the V objects and E references within `max_depth` steps (each object is expanded
once), and O(V) memory for `seen` and `parent`.

## Another way

`gc.get_referrers(obj)` walks the other way ("who points at me?"), but it scans every object the
collector tracks, so it is much slower and also finds the frames and lists of your own search.
For real debugging of leaks, `gc.set_debug(gc.DEBUG_SAVEALL)` makes the collector keep what it
frees in `gc.garbage` so you can inspect it, and the third-party `objgraph` package draws
referent graphs like the ones this function walks. The best fix for an accidental cycle is
usually a `weakref` (a child stores `weakref.ref(parent)`, a callback list stores
`weakref.WeakMethod`), which removes the cycle so plain reference counting frees the objects
right away.
