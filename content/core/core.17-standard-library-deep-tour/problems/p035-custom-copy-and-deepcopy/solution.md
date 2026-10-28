## Approach

`copy` looks for the special methods `__copy__` and `__deepcopy__` and lets the class decide.

- **Make an empty instance of the right class.** `type(self).__new__(type(self))` creates the
  object without calling `__init__`, and `type(self)` makes it a `Draft` when `self` is a `Draft`.
- **Shallow copy.** Start from the same attribute values (`__dict__.update`), then give the copy its
  own `lines` and `tags` lists and a fresh cache. Strings inside are immutable, so `list(...)`
  (a shallow copy of each list) is enough.
- **Deep copy.** `memo` is a dict from `id(original)` to its copy, shared by the whole
  `deepcopy` call. Register the new object in it **first**; then, when a cycle leads back to this
  document, `deepcopy` finds the new object in `memo` instead of starting another copy. Every
  attribute goes through `copy.deepcopy(value, memo)` (passing `memo` on is what keeps shared
  objects shared), except `owner` (kept) and `_cache` (reset).

## Code

```python
    def __copy__(self) -> "Document":
        new = type(self).__new__(type(self))
        new.__dict__.update(self.__dict__)
        new.lines = list(self.lines)
        new.tags = list(self.tags)
        new._cache = {}
        return new

    def __deepcopy__(self, memo: dict[int, object]) -> "Document":
        new = type(self).__new__(type(self))
        memo[id(self)] = new
        for key, value in self.__dict__.items():
            if key == "owner":
                new.owner = value
            elif key == "_cache":
                new._cache = {}
            else:
                setattr(new, key, copy.deepcopy(value, memo))
        return new
```

## Complexity

`__copy__` is O(number of attributes + lines + tags). `__deepcopy__` is O(size of everything
reachable), and each object is copied once thanks to `memo`.

## Another way

Put the shared object into `memo` before deep-copying: `memo[id(self.owner)] = self.owner`. Then
`deepcopy` "finds" the owner already copied (as itself) and you could deep-copy `__dict__` in one
call: `new.__dict__.update(copy.deepcopy(self.__dict__, memo))`, then reset `_cache`. It is
shorter but more surprising to read. For simpler classes, `__getstate__`/`__setstate__` also
control copying (and pickling).
