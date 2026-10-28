## Hint 1

Which five methods does `MutableMapping` require? (`__getitem__`, `__setitem__`, `__delitem__`, `__iter__`, `__len__`.) Everything else is built from them. If the inner dict maps `key.lower()` to a pair `(original_key, value)`, what does each of the five methods become?

## Hint 2

`__iter__` must yield the **original** spellings: `(orig for orig, _ in self._store.values())`. `__len__` is `len(self._store)`. In `__getitem__` and `__delitem__`, catch the inner `KeyError` and re-raise `KeyError(key)` with the caller's key (use `from None` to hide the lowercased one). The constructor can simply call `self.update(data or {}, **kwargs)`.

## Hint 3

```
_norm(key): TypeError unless str; return key.lower()
__getitem__: return store[norm(key)][1]           (KeyError(key) if missing)
__setitem__: store[norm(key)] = (key, value)
__delitem__: del store[norm(key)]
__contains__: isinstance(key, str) and key.lower() in store   # no TypeError
__eq__: if other is not a mapping: NotImplemented
        compare {lower: value} of self with {norm(k): v} of other
copy(): CaseInsensitiveDict(self)
```
