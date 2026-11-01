## Hint 1

Write the probe loop once and use it everywhere. Which three kinds of slot can it meet, and
what should each one mean for a *lookup*? Why is it wrong to stop at a tombstone? (Draw slots
1 and 2 holding keys 1 and 9, then delete 1.)
For an insert, why must you first do a full lookup before choosing where to put the new key?

## Hint 2

```
lookup(key, h):                       -> (slot, entry_index) or (None, None)
    slot = h & (cap - 1)
    loop:
        ix = indices[slot]
        if ix is None: return absent
        if ix is not DELETED:
            sh, sk, _ = entries[ix]
            if sk is key or (sh == h and sk == key): return slot, ix
        slot = (slot + 1) & (cap - 1)

setitem(key, value):
    h = hash(key); found = lookup(key, h)
    if found: entries[ix][2] = value; return
    if len(entries) + 1 > cap * 2 // 3: resize()
    entries.append([h, key, value])
    indices[first slot on h's path that is None or DELETED] = len(entries) - 1

resize():
    live = entries without None
    cap = 8; while len(live) + 1 > cap * 2 // 3: cap *= 2
    indices = [None] * cap; entries = live
    for ix, entry in enumerate(live): put ix in the first None slot on entry's path
```

Keep a separate counter of live keys for `__len__`, or count the non-`None` entries.
