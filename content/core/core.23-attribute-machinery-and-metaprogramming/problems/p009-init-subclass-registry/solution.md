## Approach

`__init_subclass__` runs once per subclass, right after the class object is built, which is the
perfect moment to register it. The registry is a class attribute of `Plugin`; writing through
`Plugin.registry` makes it obvious there is one dict for everyone. Raising inside the hook
aborts the `class` statement, so a duplicate never becomes a usable class.

## Code

```python
class Plugin:
    registry = {}
    key = None

    def __init_subclass__(cls, /, key=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if key is None:
            return
        if key in Plugin.registry:
            raise ValueError(f"duplicate plugin key {key!r} (already used by {Plugin.registry[key].__name__})")
        cls.key = key
        Plugin.registry[key] = cls

    @classmethod
    def create(cls, key, *args, **kwargs):
        try:
            plugin_class = Plugin.registry[key]
        except KeyError:
            known = ", ".join(sorted(Plugin.registry))
            raise KeyError(f"no plugin {key!r}; known: {known}") from None
        return plugin_class(*args, **kwargs)
```

## Complexity

Registration and `create` are O(1) dict operations.

## Another way

A class decorator does the same job explicitly:

```python
def register(key):
    def deco(cls):
        if key in REGISTRY:
            raise ValueError(key)
        REGISTRY[key] = cls
        return cls
    return deco

@register("csv")
class CsvExporter: ...
```

The decorator is visible at every plugin (good for readers) but can be forgotten; the
`__init_subclass__` version registers every subclass automatically. A metaclass could do it
too, but it is heavier and causes conflicts with other metaclasses; `__init_subclass__` was added
in Python 3.6 precisely so that simple cases like this one do not need a metaclass.

The `/` in the signature makes `cls` positional-only, so a class keyword that happens to be
called `cls` could never clash with it.
