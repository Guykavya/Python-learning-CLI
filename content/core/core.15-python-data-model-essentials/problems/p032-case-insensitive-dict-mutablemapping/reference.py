from collections.abc import MutableMapping


class CaseInsensitiveDict(MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._store = {}          # lowercase key -> (original key, value)
        self.update(data or {}, **kwargs)

    @staticmethod
    def _norm(key):
        if not isinstance(key, str):
            raise TypeError(f"keys must be strings, not {type(key).__name__}")
        return key.lower()

    def __getitem__(self, key):
        try:
            return self._store[self._norm(key)][1]
        except KeyError:
            raise KeyError(key) from None

    def __setitem__(self, key, value):
        self._store[self._norm(key)] = (key, value)

    def __delitem__(self, key):
        try:
            del self._store[self._norm(key)]
        except KeyError:
            raise KeyError(key) from None

    def __iter__(self):
        return (original for original, _ in self._store.values())

    def __len__(self):
        return len(self._store)

    def __contains__(self, key):
        return isinstance(key, str) and key.lower() in self._store

    def __eq__(self, other):
        if not isinstance(other, MutableMapping) and not isinstance(other, dict):
            return NotImplemented
        try:
            mine = {k: v for k, (_, v) in self._store.items()}
            theirs = {self._norm(k): v for k, v in other.items()}
        except TypeError:
            return False
        return mine == theirs

    def copy(self):
        return CaseInsensitiveDict(self)

    def __repr__(self):
        return f"CaseInsensitiveDict({dict(self.items())!r})"
