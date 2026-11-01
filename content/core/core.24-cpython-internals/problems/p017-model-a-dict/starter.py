DELETED = object()   # tombstone marker for self.indices


class ToyDict:
    """A model of CPython's compact dict: entries in insertion order + a probing index table."""

    def __init__(self):
        self.indices = [None] * 8
        self.entries = []

    @property
    def capacity(self):
        return len(self.indices)

    def __setitem__(self, key, value):
        # TODO: update in place, or (resize if needed and) add a new entry
        pass

    def __getitem__(self, key):
        # TODO: probe; None ends the search, DELETED is skipped
        raise KeyError(key)

    def __delitem__(self, key):
        # TODO: tombstone in indices, None in entries
        raise KeyError(key)

    def __contains__(self, key):
        return False

    def __len__(self):
        return 0

    def __iter__(self):
        return iter([])

    def get(self, key, default=None):
        return default

    def items(self):
        return []
