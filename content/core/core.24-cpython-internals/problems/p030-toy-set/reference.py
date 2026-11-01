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
