import weakref


class Cache:
    """Share objects while they are in use; forget them when nobody holds them."""

    def __init__(self, factory):
        self.factory = factory
        self.hits = 0
        self.misses = 0
        # TODO: a WeakValueDictionary for the entries

    def get(self, key):
        # TODO: hit if a live object exists, otherwise create, store and return it
        raise NotImplementedError

    def __len__(self):
        return 0

    def __contains__(self, key):
        return False
