## Approach

Keep the dict and the dotted path of this level. `__getattr__` is the fallback for every name
the object does not have itself: look the name up in the dict, wrap dict values in a new
`Config` that carries the longer path, and translate `KeyError` into `AttributeError` (the
attribute protocol's "not here" signal, which `hasattr`, `getattr` with a default and many
libraries rely on). `__dir__` adds the keys to the normal list. `to_dict` copies recursively.

## Code

```python
def _plain(value):
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


class Config:
    def __init__(self, data, path=""):
        self._data = data
        self._path = path

    def __getattr__(self, name):
        data = vars(self).get("_data", {})
        full = f"{vars(self).get('_path', '')}.{name}".lstrip(".")
        try:
            value = data[name]
        except KeyError:
            raise AttributeError(f"no config key {full!r}") from None
        if isinstance(value, dict):
            return Config(value, full)
        return value

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(self._data))

    def to_dict(self):
        return _plain(self._data)
```

Reading `_data` through `vars(self)` instead of `self._data` is a safety habit: if a `Config`
is ever built without `__init__` (by `copy` or `pickle`), `self._data` inside `__getattr__`
would call `__getattr__` again forever.

## Complexity

Each dotted step is one dict lookup, O(1), plus creating a small wrapper. `to_dict` is
O(total size of the data).

## Another way

`copy.deepcopy(self._data)` is a one-line `to_dict` that also copies sets, tuples of lists
and so on. Another design converts everything **once** in `__init__` (nested dicts become
nested `Config` objects stored as real attributes, `self.__dict__.update(...)`); then no
`__getattr__` is needed at all, at the cost of copying up front. The standard library's
`types.SimpleNamespace(**d)` does that for one level.
