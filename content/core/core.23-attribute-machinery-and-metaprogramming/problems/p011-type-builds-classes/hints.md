## Hint 1

The `namespace` dict is exactly what a class body would produce: `"__slots__"` mapped to a
tuple, `"__init__"` mapped to a function, and so on. Can you write `def __init__(self, *values)`
as an ordinary nested function inside `make_record_class` and put it into the dict? How does
that function know the field names? (It is a closure.)

## Hint 2

```
make_record_class(name, fields):
    fields = tuple(fields)                     # private copy

    def __init__(self, *values):
        if len(values) != len(fields): raise TypeError(...)
        for field, value in zip(fields, values): setattr(self, field, value)

    def __repr__(self):  "Name(" + ", ".join(f"{f}={getattr(self, f)!r}") + ")"

    def __eq__(self, other):
        if type(other) is not type(self): return NotImplemented
        compare every field

    return type(name, (), {"__slots__": fields, "__init__": __init__, ...})
```
