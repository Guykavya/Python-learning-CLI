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
