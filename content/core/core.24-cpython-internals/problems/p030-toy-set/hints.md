## Hint 1

Write `_find(item, h)` first, and build everything else on it. While probing, what are the three
kinds of slot you can meet, and what does each one mean for a **lookup**? For an **insert**, why
is the first tombstone a good place to write, but not a reason to stop probing? (Think of
`add(a); add(b); remove(a); add(b)` where `a` and `b` collide.)

Why does `fill` (live + tombstones) decide when to resize, while `used` (live only) decides the
new size? What would happen to a lookup for a missing item if every slot were either live or a
tombstone?

## Hint 2

```
_find(item, h):                      -> (index of item or None, index to insert at)
    i = h & (capacity - 1); free = None
    loop:
        e = slots[i]
        if e is None:      return None, (free if free is not None else i)
        if e is _DELETED:  if free is None: free = i
        elif e[0] == h and (e[1] is item or e[1] == item): return i, None
        i = (i + 1) & (capacity - 1)

add(item):
    h = hash(item); found, free = _find(item, h)
    if found is not None: return
    if (fill + 1) * 3 > capacity * 2: _resize(); found, free = _find(item, h)
    if slots[free] is None: fill += 1           # reusing a tombstone does not change fill
    slots[free] = (h, item); used += 1

discard(item):  found = _find(...)[0]; if found is not None: slots[found] = _DELETED; used -= 1

_resize():
    live = [entries that are tuples]
    capacity = 8; while (len(live) + 1) * 3 > capacity * 2: capacity *= 2
    new empty slots; put each (h, item) at its first None slot from h & (capacity - 1)
    fill = used = len(live)
```
