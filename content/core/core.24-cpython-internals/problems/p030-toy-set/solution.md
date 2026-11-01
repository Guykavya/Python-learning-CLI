## Approach

Everything rests on one probing function, `_find(item, h)`, which answers two questions in one
walk along the chain: *where is the item?* and *where could it be inserted?* It walks from
`h & mask`, remembers the first tombstone, and stops at the first empty slot. If it saw the item,
it returns that index; otherwise it returns the first tombstone (reusing space) or the empty slot.

Two counters keep the table healthy. `used` counts live items. `fill` also counts tombstones,
because they occupy slots that probes must walk through. Resizing is triggered by `fill` (so there
is always an empty slot to end every probe) and sized by `used` (so tombstones are dropped and
add/remove cycles do not make the table grow). This is the same split as CPython's `used` and
`fill` fields in `setobject.c`.

## Code

```python
"""ToySet: a hash set with open addressing and linear probing, modelled on CPython's set."""

_DELETED = object()  # tombstone: "something was here, keep probing"


class ToySet:
    def __init__(self, items=()):
        self._capacity = 8
        self._slots = [None] * self._capacity  # None, _DELETED, or (hash, item)
        self._used = 0                         # live items
        self._fill = 0                         # live items + tombstones
        for item in items:
            self.add(item)

    @property
    def capacity(self):
        return self._capacity

    # ------------------------------------------------------------ probing
    def _find(self, item, h):
        """(index of item or None, index where it could be inserted)."""
        mask = self._capacity - 1
        index = h & mask
        free = None
        while True:
            entry = self._slots[index]
            if entry is None:
                return None, (index if free is None else free)
            if entry is _DELETED:
                if free is None:
                    free = index
            else:
                stored_hash, stored = entry
                if stored_hash == h and (stored is item or stored == item):
                    return index, None
            index = (index + 1) & mask

    def _resize(self):
        live = [entry for entry in self._slots if entry is not None and entry is not _DELETED]
        capacity = 8
        while (len(live) + 1) * 3 > capacity * 2:
            capacity *= 2
        self._capacity = capacity
        self._slots = [None] * capacity
        self._fill = self._used = len(live)
        mask = capacity - 1
        for entry in live:
            index = entry[0] & mask
            while self._slots[index] is not None:
                index = (index + 1) & mask
            self._slots[index] = entry

    # ------------------------------------------------------------ basic operations
    def add(self, item):
        h = hash(item)
        found, free = self._find(item, h)
        if found is not None:
            return
        if (self._fill + 1) * 3 > self._capacity * 2:
            self._resize()
            found, free = self._find(item, h)
        if self._slots[free] is None:
            self._fill += 1  # a tombstone reused does not change fill
        self._slots[free] = (h, item)
        self._used += 1

    def discard(self, item):
        found, _ = self._find(item, hash(item))
        if found is not None:
            self._slots[found] = _DELETED
            self._used -= 1

    def remove(self, item):
        if item not in self:
            raise KeyError(item)
        self.discard(item)

    def __contains__(self, item):
        return self._find(item, hash(item))[0] is not None

    def __len__(self):
        return self._used

    def __iter__(self):
        for entry in self._slots:
            if entry is not None and entry is not _DELETED:
                yield entry[1]

    def __repr__(self):
        return f"ToySet({list(self)!r})"

    # ------------------------------------------------------------ set algebra
    def union(self, other):
        result = ToySet(self)
        for item in other:
            result.add(item)
        return result

    def intersection(self, other):
        other = other if isinstance(other, (ToySet, set, frozenset)) else ToySet(other)
        return ToySet(item for item in self if item in other)

    def difference(self, other):
        other = other if isinstance(other, (ToySet, set, frozenset)) else ToySet(other)
        return ToySet(item for item in self if item not in other)

    __or__ = union
    __and__ = intersection
    __sub__ = difference

    def __eq__(self, other):
        if not isinstance(other, (ToySet, set, frozenset)):
            return NotImplemented
        return len(self) == len(other) and all(item in other for item in self)
```

## Complexity

With the load kept at most 2/3, `add`, `discard` and `in` take O(1) on average: the expected
probe length is a small constant. The worst case is O(n), when many items share a hash (like the
tests' `Collide` class), which is why good `__hash__` methods matter. A resize is O(n), but it
happens only after the table doubled its contents, so `add` is **amortised O(1)**, like
`list.append`. `union` is O(len(a) + len(b)); `intersection` and `difference` are O(len(a)) after
turning `other` into a set if needed.

## Another way

CPython does not probe linearly forever. It checks a few neighbouring slots (cheap, cache
friendly), then jumps using a **perturbation** of the hash, so that items with similar hashes
(for example consecutive ints) do not form long clusters:

```python
def _probe(self, h):
    mask = self._capacity - 1
    perturb = h & ((1 << 64) - 1)   # treat the hash as unsigned
    i = h & mask
    while True:
        yield i
        perturb >>= 5
        i = (5 * i + 1 + perturb) & mask
```

Once `perturb` reaches 0, `i = 5 * i + 1` visits every slot of a power-of-two table, so a probe
always reaches an empty slot. Storing hashes and items in two parallel lists instead of tuples
also works and saves creating a tuple per item.
