## Approach

This is a graph walk: objects are nodes, "contains" is an edge. Remember visited objects by
`id()`, which works for unhashable containers and treats equal-but-separate objects as
different, which is what memory use needs. An explicit `todo` list instead of recursion means a
deeply nested structure cannot hit the recursion limit.

## Code

```python
import sys

CONTAINERS = (list, tuple, set, frozenset)


def deep_size(obj):
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
```

## Complexity

O(n) time and space, where n is the number of reachable objects plus references.

## Another way

Recursion with a shared `seen` set reads more naturally:

```python
def deep_size(obj, seen=None):
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, CONTAINERS):
        size += sum(deep_size(x, seen) for x in obj)
    return size
```

It fails with `RecursionError` on a list nested about 1,000 levels deep. For real measurements
of a whole program, `tracemalloc` (core.20) counts actual allocations, which is more honest than
adding up `getsizeof` values. Note also that objects such as small ints and interned strings are
shared with the rest of the program, so "deep size" is an upper bound on what you would free.
