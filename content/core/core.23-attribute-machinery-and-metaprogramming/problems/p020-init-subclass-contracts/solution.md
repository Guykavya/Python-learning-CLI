## Approach

`type.__new__` calls `__init_subclass__` on the parent with the freshly created class, before
the class statement finishes. Raising there stops the class from being bound to its name, so
a broken subclass never exists. Use `hasattr` so inherited values count. Keywords in the class
line (`abstract=True`, `tag=...`) arrive as keyword arguments; take yours and pass the rest to
`super().__init_subclass__`, which ends at `object.__init_subclass__`, and that one rejects any
leftover keyword with `TypeError`.

`abstract` is just a parameter, so it is not remembered: the next subclass gets the default
`False` and is checked.

`__init__` and `__repr__` live on `Record`; normal inheritance gives them to every subclass,
and a subclass's own `__repr__` simply wins in the MRO.

## Code

```python
REQUIRED = ("table", "fields")


class Record:
    def __init_subclass__(cls, /, abstract=False, **kwargs):
        super().__init_subclass__(**kwargs)
        if abstract:
            return
        missing = sorted(name for name in REQUIRED if not hasattr(cls, name))
        if missing:
            raise TypeError(f"{cls.__name__} is missing class attribute(s): {', '.join(missing)}")
        if not isinstance(cls.table, str) or not cls.table:
            raise TypeError(f"{cls.__name__}.table must be a non-empty str")
        fields = cls.fields
        if not isinstance(fields, tuple) or not fields or not all(isinstance(f, str) for f in fields):
            raise TypeError(f"{cls.__name__}.fields must be a non-empty tuple of str")
        if len(set(fields)) != len(fields):
            raise TypeError(f"{cls.__name__}.fields has duplicate names")

    def __init__(self, **values):
        name = type(self).__name__
        missing = [f for f in self.fields if f not in values]
        if missing:
            raise TypeError(f"{name} missing field(s): {', '.join(missing)}")
        unknown = [key for key in values if key not in self.fields]
        if unknown:
            raise TypeError(f"{name} got unknown field(s): {', '.join(unknown)}")
        for field in self.fields:
            setattr(self, field, values[field])

    def __repr__(self):
        args = ", ".join(f"{f}={getattr(self, f)!r}" for f in self.fields)
        return f"{type(self).__name__}({args})"
```

The `/` makes `cls` positional-only, so a class keyword that happens to be called `cls`
cannot clash with it.

## Complexity

The check runs once per class definition: O(number of fields). Each instance creation is
O(fields) (the `in self.fields` tests on a short tuple).

## Another way

Generate the methods per class inside `__init_subclass__`, only when the class did not write
its own:

```python
if "__repr__" not in cls.__dict__:
    def __repr__(self):
        args = ", ".join(f"{f}={getattr(self, f)!r}" for f in self.fields)
        return f"{type(self).__name__}({args})"
    cls.__repr__ = __repr__
```

That is how `dataclass` works (it writes methods onto the class). For this problem the
inherited method is simpler and does the same thing. A metaclass could also do the checks,
but `__init_subclass__` is the lighter tool: no metaclass conflicts, and it reads like a
normal method.
