- Forgetting to inherit from `ABC` (or to import `abstractmethod`). Without `ABC`, `@abstractmethod`
  is not enforced and `Storage()` works.
- Writing `get_or` in `MemoryStorage` with `self._data.get(...)`. It works there, but every other
  storage must then write it again; it belongs in the base class.
- `contains` written as `return self.get_or(key) is not None`. A key whose value is `None` would
  look missing.
- `PrefixStorage(MemoryStorage)`: inheriting from a concrete storage instead of wrapping one. Then
  it can only ever prefix a memory storage, and it has a second, unused `_data` dict.
- Forgetting to strip the prefix in `keys()`. Then `users.get(users.keys()[0])` adds the prefix
  twice and fails.
- `def __init__(self, initial={})` with `self._data = initial`. All storages share one dict.
- Letting the inner `KeyError('user:zoya')` escape. The caller of `users` never used that long key.
