## Approach

`@something` before a class works exactly like before a function: the decorator is called with the class and its return value replaces the name. A class decorator can therefore register the class somewhere (a side effect) and return it unchanged, or change it (add a method) and return it.

`Registry` supports two call shapes with one method. That is the standard trick: make the positional parameter optional. With `cls=None` we know we were called as `@reg(name="x")` and must return a decorator; otherwise we were called as `@reg` and finish the job directly.

`auto_repr` builds a function inside the decorator and attaches it to the class with `cls.__repr__ = ...`. Special methods are looked up on the class, so adding the function there is enough for `repr(obj)` to find it.

## Code

```python
class Registry:
    def __init__(self):
        self._classes = {}

    def __call__(self, cls=None, *, name=None):
        def decorate(klass):
            key = name if name is not None else klass.__name__.lower()
            if key in self._classes:
                raise ValueError(f"name {key!r} is already registered")
            self._classes[key] = klass
            klass.registered_name = key
            return klass

        if cls is None:          # used as @registry(name="x")
            return decorate
        return decorate(cls)     # used as @registry

    def __getitem__(self, name):
        try:
            return self._classes[name]
        except KeyError:
            raise KeyError(f"nothing registered as {name!r}") from None

    def __contains__(self, name):
        return name in self._classes

    def __len__(self):
        return len(self._classes)

    def names(self):
        return sorted(self._classes)


def auto_repr(cls):
    def __repr__(self):
        parts = ", ".join(f"{field}={getattr(self, field)!r}" for field in cls._fields)
        return f"{type(self).__name__}({parts})"

    cls.__repr__ = __repr__
    return cls
```

## Complexity

Registering and lookup are O(1). `auto_repr`'s repr is O(number of fields).

## Another way

Define `__init_subclass__` on a base class so every subclass registers itself without any decorator (covered in a later metaprogramming module), or use `dataclasses.dataclass`, which is a class decorator that generates `__repr__`, `__eq__` and `__init__` for you (next section of this module).
