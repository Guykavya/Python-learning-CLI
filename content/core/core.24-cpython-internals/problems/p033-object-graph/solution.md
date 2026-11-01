## Approach

Breadth-first search with `gc.get_referents` as the neighbour function. The `kind` function
prunes the graph: atoms (strings, numbers) have no interesting referents, and types, functions
and modules would drag in the whole program, so they never enter the queue. Plain dicts are
"transparent": they are walked through but not reported, which hides the version-dependent
question of whether an instance's attributes live in a separate dict object. Objects are
remembered by `id()` the moment they are queued, so each one is processed once even if it is
reachable along many paths.

## Code

```python
"""Walk the object graph with gc.get_referents and summarise what a root keeps alive."""

import gc
import types
from collections import Counter, deque

CONTAINERS = (list, tuple, set, frozenset)
NEVER_FOLLOW = (type, types.FunctionType, types.BuiltinFunctionType, types.MethodType, types.ModuleType)


def kind(obj):
    """'follow' for plain dicts, 'count' for containers and user objects, None for everything else."""
    if type(obj) is dict:
        return "follow"
    if type(obj) in CONTAINERS:
        return "count"
    if isinstance(obj, NEVER_FOLLOW) or type(obj).__module__ == "builtins":
        return None
    return "count"


def reachable(root, max_nodes=10_000):
    """Containers and user objects reachable from root, breadth-first, each once, at most max_nodes."""
    found = []
    seen = {id(root)}
    queue = deque([root])
    while queue and len(found) < max_nodes:
        obj = queue.popleft()
        what = kind(obj)
        if what is None:
            continue
        if what == "count":
            found.append(obj)
        for ref in gc.get_referents(obj):
            if id(ref) not in seen and kind(ref) is not None:
                seen.add(id(ref))
                queue.append(ref)
    return found


def summary(root, max_nodes=10_000):
    """Counter {type name: how many} of reachable(root, max_nodes)."""
    return Counter(type(obj).__name__ for obj in reachable(root, max_nodes))
```

## Complexity

O(V + E) for V reachable objects and E references between them (each object's referents are
listed once). `max_nodes` caps the work for huge graphs. Memory: the `seen` set and the queue,
O(V).

## Another way

A depth-first walk with an explicit stack (`stack.pop()` instead of `queue.popleft()`) finds the
same set of objects in a different order. To find *who* keeps an object alive, walk the other
direction with `gc.get_referrers(obj)`; that is how leak hunters trace an object back to the
global or the cache that holds it. Real tools such as `objgraph` and `pympler` do exactly this, and
`tracemalloc` (core.20) answers the related question *where* the memory was allocated.

To estimate the memory a root retains, sum `sys.getsizeof` over `reachable(root)` **plus** the
dicts you walked through; the number is version dependent, so use it to compare, never as an
exact budget.
