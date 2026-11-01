## Approach

Everything rests on one probe loop. A lookup walks the probe path and stops only at a free slot
(`None`); it skips tombstones, because a key that collided with a deleted key was placed *after*
it. The match test checks identity first (cheap and also correct for objects such as
`float("nan")` that are not equal to themselves), then compares the stored hash before calling
`==`, so most non-matching slots are rejected without running `__eq__`.

Adding a key always appends to `entries`, which gives insertion order for free. The slot is the
first free or tombstone slot on its path, but only after a full lookup proved the key absent;
otherwise a key stored past a tombstone would get a duplicate.

Deleting cannot empty the slot (`None` would cut other keys' probe paths), so it leaves a
tombstone. `entries` keeps a `None` hole. Holes and tombstones are cleaned up by the next resize,
which is triggered by `len(entries)`: holes count against the 2/3 limit until then, just like in
CPython, where deletions do not give the space back.

## Code

```python
DELETED = object()


class ToyDict:
    def __init__(self):
        self.indices = [None] * 8
        self.entries = []
        self._live = 0

    @property
    def capacity(self):
        return len(self.indices)

    def _probe(self, h):
        mask = self.capacity - 1
        slot = h & mask
        while True:
            yield slot
            slot = (slot + 1) & mask

    def _lookup(self, key, h):
        for slot in self._probe(h):
            ix = self.indices[slot]
            if ix is None:
                return None, None
            if ix is DELETED:
                continue
            stored_hash, stored_key, _ = self.entries[ix]
            if stored_key is key or (stored_hash == h and stored_key == key):
                return slot, ix

    def _free_slot(self, h):
        for slot in self._probe(h):
            if self.indices[slot] is None or self.indices[slot] is DELETED:
                return slot

    def _resize(self):
        live = [entry for entry in self.entries if entry is not None]
        capacity = 8
        while len(live) + 1 > capacity * 2 // 3:
            capacity *= 2
        self.indices = [None] * capacity
        self.entries = live
        for ix, (h, _, _) in enumerate(live):
            self.indices[self._free_slot(h)] = ix

    def __setitem__(self, key, value):
        h = hash(key)
        _, ix = self._lookup(key, h)
        if ix is not None:
            self.entries[ix][2] = value
            return
        if len(self.entries) + 1 > self.capacity * 2 // 3:
            self._resize()
        self.entries.append([h, key, value])
        self.indices[self._free_slot(h)] = len(self.entries) - 1
        self._live += 1

    def __getitem__(self, key):
        _, ix = self._lookup(key, hash(key))
        if ix is None:
            raise KeyError(key)
        return self.entries[ix][2]

    def __delitem__(self, key):
        slot, ix = self._lookup(key, hash(key))
        if ix is None:
            raise KeyError(key)
        self.indices[slot] = DELETED
        self.entries[ix] = None
        self._live -= 1

    def __contains__(self, key):
        return self._lookup(key, hash(key))[1] is not None

    def __len__(self):
        return self._live

    def __iter__(self):
        for entry in self.entries:
            if entry is not None:
                yield entry[1]

    def get(self, key, default=None):
        _, ix = self._lookup(key, hash(key))
        return default if ix is None else self.entries[ix][2]

    def items(self):
        return [(entry[1], entry[2]) for entry in self.entries if entry is not None]
```

The loops always end: the table is never more than 2/3 full, so every probe path reaches a
`None` slot.

## Complexity

Average O(1) for get, set and delete while the hashes spread well, because the load factor
stays at or below 2/3. With many colliding hashes (the `Collide` class) every key shares one
path and operations become O(n). A resize is O(n), but capacities double, so its cost averaged
over the inserts is O(1), the same argument as for list over-allocation. Iteration is
O(len(entries)).

## Another way

CPython's real probe sequence is not linear. It uses
`slot = (5 * slot + 1 + perturb) & mask` with `perturb >>= 5` after each step, so the high
bits of the hash also take part and keys with similar hashes (such as consecutive ints) do not
form one long run of occupied slots. You can drop that into `_probe`:

```python
def _probe(self, h):
    mask = self.capacity - 1
    perturb = h & 0xFFFFFFFFFFFFFFFF      # CPython treats the hash as unsigned
    slot = perturb & mask
    while True:
        yield slot
        perturb >>= 5
        slot = (slot * 5 + perturb + 1) & mask
```

The rest of the class stays the same. Slot numbers then differ from the layout tests, but the
dict behaves identically. Real CPython also stores the index array in 1, 2, 4 or 8 bytes per slot
depending on the capacity, which is why the compact dict uses much less memory than the old
one-big-table design.
