import sys

CONTAINERS = (list, tuple, set, frozenset)


def deep_size(obj):
    """Bytes of obj plus everything reachable through list/tuple/set/frozenset/dict, each once."""
    seen = set()
    total = 0
    todo = [obj]
    while todo:
        item = todo.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        total += sys.getsizeof(item)
        if isinstance(item, dict):
            todo.extend(item.keys())
            todo.extend(item.values())
        elif isinstance(item, CONTAINERS):
            todo.extend(item)
    return total
