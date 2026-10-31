from collections.abc import MutableMapping


class CaseInsensitiveDict(MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._store = {}

    def __getitem__(self, key):
        raise KeyError(key)

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return iter([])

    def __len__(self):
        return 0
