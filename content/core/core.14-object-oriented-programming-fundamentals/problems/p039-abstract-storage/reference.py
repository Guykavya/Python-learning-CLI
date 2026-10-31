from abc import ABC, abstractmethod


class Storage(ABC):
    """The interface every storage backend must offer."""

    @abstractmethod
    def get(self, key):
        """Return the value for key, or raise KeyError."""

    @abstractmethod
    def set(self, key, value):
        """Store value under key."""

    @abstractmethod
    def delete(self, key):
        """Remove key, or raise KeyError."""

    @abstractmethod
    def keys(self):
        """Return a list of all keys."""

    # Concrete methods: built only on the four abstract ones.

    def get_or(self, key, default=None):
        try:
            return self.get(key)
        except KeyError:
            return default

    def contains(self, key):
        try:
            self.get(key)
        except KeyError:
            return False
        return True

    def pop(self, key):
        value = self.get(key)
        self.delete(key)
        return value

    def items(self):
        return [(key, self.get(key)) for key in sorted(self.keys())]

    def update(self, pairs):
        for key, value in pairs.items():
            self.set(key, value)

    def count(self):
        return len(self.keys())


class MemoryStorage(Storage):
    def __init__(self, initial=None):
        self._data = dict(initial) if initial is not None else {}

    def get(self, key):
        return self._data[key]

    def set(self, key, value):
        self._data[key] = value

    def delete(self, key):
        del self._data[key]

    def keys(self):
        return list(self._data)


class PrefixStorage(Storage):
    def __init__(self, inner, prefix):
        if not isinstance(inner, Storage):
            raise TypeError(f"inner must be a Storage, got {type(inner).__name__}")
        if not isinstance(prefix, str) or not prefix:
            raise ValueError("prefix must be a non-empty string")
        self._inner = inner
        self._prefix = prefix

    def get(self, key):
        try:
            return self._inner.get(self._prefix + key)
        except KeyError:
            raise KeyError(key) from None

    def set(self, key, value):
        self._inner.set(self._prefix + key, value)

    def delete(self, key):
        try:
            self._inner.delete(self._prefix + key)
        except KeyError:
            raise KeyError(key) from None

    def keys(self):
        n = len(self._prefix)
        return [key[n:] for key in self._inner.keys() if key.startswith(self._prefix)]
