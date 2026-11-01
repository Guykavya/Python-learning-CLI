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

    def _find(self, item, h):
        """Return (index of item or None, index where it could be inserted)."""
        raise NotImplementedError

    def _resize(self):
        raise NotImplementedError

    def add(self, item):
        raise NotImplementedError

    def discard(self, item):
        raise NotImplementedError

    def remove(self, item):
        raise NotImplementedError

    def __contains__(self, item):
        raise NotImplementedError

    def __len__(self):
        return self._used

    def __iter__(self):
        raise NotImplementedError

    # TODO: union, intersection, difference, |, &, -, __eq__
