## Hint 1

When exactly does Python call `__getattr__`? (Only after normal lookup has failed.) So
`_data`, `to_dict` and `__dir__` are found normally, and every other name lands in
`__getattr__(self, name)`. What do you return when the value is a dict, and what must you
raise instead of the `KeyError` that `self._data[name]` gives?

## Hint 2

```
__init__(data, path=""):  keep data and path

__getattr__(name):
    full = path + "." + name   (just name at the top)
    try: value = data[name]
    except KeyError: raise AttributeError(f"no config key {full!r}") from None
    if value is a dict: return Config(value, full)
    return value

__dir__():  sorted(set(super().__dir__()) | set(data))
to_dict():  copy recursively: dict -> {k: copy(v)}, list -> [copy(v)], else v
```
