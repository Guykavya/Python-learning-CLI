## Approach

**An abstract base class is a contract** (chapter section 16). `Storage` says "every storage has
`get`, `set`, `delete` and `keys`", and Python enforces it: a class that still has an abstract
method cannot be instantiated. You find the mistake at the moment you create the object, not later
when some rarely used method is called.

**Write shared logic once, on top of the contract.** `get_or`, `contains`, `pop`, `items`, `update`
and `count` call only the four abstract methods. So they work for `MemoryStorage`, `PrefixStorage`,
and even the test's `ListStorage`, which the solution has never seen. This is the template method
idea: the base class has the algorithm, subclasses fill in the basic steps (section 10).

`contains` uses EAFP: try `get` and catch `KeyError` (section 15). Testing the value
(`self.get_or(key) is not None`) would be wrong for keys whose value is `None`.

**`PrefixStorage` is composition and inheritance at once.** It *has* an inner storage
(composition, section 14) and *is* a storage (it inherits the interface). Because it is a
`Storage`, it can be wrapped again, and it gets all concrete methods for free. Its `isinstance(inner,
Storage)` check is one of the good uses of `isinstance`: checking against an ABC, not a concrete
class.

## Code

```python
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
```

`raise KeyError(key) from None` replaces the inner error (which shows the long key) and hides it
from the traceback (section 18).

## Complexity

For `MemoryStorage`, `get`, `set`, `delete` are O(1), `keys` O(n). `items` is O(n log n) for the
sort. `PrefixStorage.keys` is O(n) over all inner keys.

## Another way

The standard library already has this idea: `collections.abc.MutableMapping` is an ABC with five
abstract methods (`__getitem__`, `__setitem__`, `__delitem__`, `__iter__`, `__len__`) that gives you
`get`, `pop`, `items`, `update` and more for free. Those special methods belong to the data model
chapter (core.15); this problem builds the same idea with plain method names.
