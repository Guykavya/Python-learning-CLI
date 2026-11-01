import weakref


class Cache:
    """Share objects while they are in use; forget them when nobody holds them."""

    def __init__(self, factory):
        self.factory = factory
        self.hits = 0
        self.misses = 0
        self._entries = weakref.WeakValueDictionary()

    def get(self, key):
        obj = self._entries.get(key)
        if obj is not None:
            self.hits += 1
            return obj
        self.misses += 1
        obj = self.factory(key)
        self._entries[key] = obj
        return obj

    def __len__(self):
        return len(self._entries)

    def __contains__(self, key):
        return key in self._entries
