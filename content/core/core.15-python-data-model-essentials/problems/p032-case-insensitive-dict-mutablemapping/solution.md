## Approach

`MutableMapping` is an abstract base class with five abstract methods. Once you define them, every other method is written in terms of them: `get` calls `__getitem__` and catches `KeyError`; `pop` calls `__getitem__` then `__delitem__`; `update` calls `__setitem__`; `items()` iterates `__iter__` and calls `__getitem__`. So the design question is only "what is the inner representation?".

The inner dict maps the **lowercase** key to `(original, value)`. Lookup and delete are one normalisation away; `__iter__` hides the lowercase key and yields the original spelling. `__setitem__` overwrites the pair, which updates the stored spelling. Overriding `__contains__` is optional, but the default one calls `__getitem__` and a non-string key would hit your `TypeError`; the override turns that into a plain `False`.

`__eq__` compares lowercase-key dicts so any mapping can be on the other side.

## Code

```python
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
```

## Complexity

Every operation is O(1) average; iteration O(n); memory O(n).

## Another way

Subclass `dict` and override `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `get`, `pop`, `setdefault`, `update`, `__init__`, `copy`: more code and easy to miss one, because built-in `dict` methods do not call each other. Another option: normalise keys with a `str` subclass whose `__hash__` and `__eq__` ignore case (but then `repr` and equality with plain strings get odd).
