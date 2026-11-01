DELETED = object()   # tombstone marker for self.indices


class ToyDict:
    """A model of CPython's compact dict: entries in insertion order + a probing index table."""

    def __init__(self):
        self.indices = [None] * 8
        self.entries = []
        self._live = 0

    @property
    def capacity(self):
        return len(self.indices)

    # --- internals -------------------------------------------------------

    def _probe(self, h):
        """Yield the slots on h's probe path (linear probing)."""
        mask = self.capacity - 1
        slot = h & mask
        while True:
            yield slot
            slot = (slot + 1) & mask

    def _lookup(self, key, h):
        """Return (slot, entry_index) for key, or (None, None) when it is absent."""
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
        """First free or tombstone slot on h's probe path."""
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

    # --- the mapping interface -------------------------------------------

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
