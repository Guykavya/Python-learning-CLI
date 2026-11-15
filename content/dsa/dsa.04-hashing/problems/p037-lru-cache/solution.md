## Approach

Use a dictionary as an ordered structure: the **end** is the most recently used, the **front** the least recently used. Popping a key and
inserting it again moves it to the end in O(1). Evicting the front key means deleting `next(iter(cache))`.

## Code

```python
c = int(input())
q = int(input())
cache = {}
out = []
for _ in range(q):
    parts = input().split()
    if parts[0] == "get":
        k = int(parts[1])
        if k in cache:
            v = cache.pop(k)
            cache[k] = v
            out.append(v)
        else:
            out.append(-1)
    else:
        k = int(parts[1])
        v = int(parts[2])
        if k in cache:
            del cache[k]
        elif len(cache) == c:
            del cache[next(iter(cache))]
        cache[k] = v
print("\n".join(map(str, out)))
```

## Complexity

O(1) average per command, O(c) memory. `next(iter(cache))` is O(1) when the oldest keys have not been deleted in bulk (CPython may skip
a few deleted slots at the front; amortised it stays cheap).

## Another way

The textbook structure is a **hash map plus a doubly linked list**: the map points to list nodes, and moving a node to the front and removing
from the back are O(1). `collections.OrderedDict` with `move_to_end` and `popitem(last=False)` packages the same idea.
