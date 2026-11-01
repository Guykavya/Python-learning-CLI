import gc
import types


def _followable(x):
    """Classes, modules and functions lead into the whole program: do not walk into them."""
    return not isinstance(x, (type, types.ModuleType, types.FunctionType))


def cycle_path(obj, max_depth=100):
    """Shortest [obj, ..., obj] path through gc.get_referents, or None."""
    parent = {}                     # id(x) -> the object x was first reached from
    seen = {}                       # id(x) -> x  (holding x keeps its id valid)
    frontier = [obj]                # everything exactly `step` steps from obj
    for step in range(max_depth):
        next_frontier = []
        for node in frontier:
            for ref in gc.get_referents(node):
                if ref is obj:
                    path = [obj]                    # walk back: obj <- node <- ... <- obj
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
    """True if obj can reach itself by following referents."""
    return cycle_path(obj, max_depth) is not None
