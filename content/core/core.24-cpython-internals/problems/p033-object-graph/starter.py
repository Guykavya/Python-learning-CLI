"""Walk the object graph with gc.get_referents and summarise what a root keeps alive."""

import gc
import types
from collections import Counter, deque

CONTAINERS = (list, tuple, set, frozenset)
NEVER_FOLLOW = (type, types.FunctionType, types.BuiltinFunctionType, types.MethodType, types.ModuleType)


def kind(obj):
    """'follow' for plain dicts, 'count' for containers and user objects, None for everything else."""
    return None


def reachable(root, max_nodes=10_000):
    """Containers and user objects reachable from root, breadth-first, each once, at most max_nodes."""
    return []


def summary(root, max_nodes=10_000):
    """Counter {type name: how many} of reachable(root, max_nodes)."""
    return Counter()
