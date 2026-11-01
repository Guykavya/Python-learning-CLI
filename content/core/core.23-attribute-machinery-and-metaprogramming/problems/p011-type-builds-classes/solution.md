## Approach

Write each method as a nested function that closes over `fields`, put them in a namespace dict
together with `__slots__`, and hand everything to `type`. `type` does the same work as a `class`
statement: it creates slot descriptors for `x` and `y`, turns off the instance `__dict__`, and
sets `__name__` and `__qualname__` from the name. `fields` is copied into a tuple first, so the
caller cannot change the class later.

## Code

```python
def make_record_class(name, fields):
    fields = tuple(fields)

    def __init__(self, *values):
        if len(values) != len(fields):
            raise TypeError(
                f"{name} expects {len(fields)} values ({', '.join(fields)}), got {len(values)}"
            )
        for field, value in zip(fields, values):
            setattr(self, field, value)

    def __repr__(self):
        parts = ", ".join(f"{field}={getattr(self, field)!r}" for field in fields)
        return f"{type(self).__name__}({parts})"

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return all(getattr(self, f) == getattr(other, f) for f in fields)

    namespace = {
        "__slots__": fields,
        "__init__": __init__,
        "__repr__": __repr__,
        "__eq__": __eq__,
    }
    return type(name, (), namespace)
```

## Complexity

Creating the class: O(number of fields). `__init__`, `__repr__` and `__eq__`: O(number of fields).

## Another way

A `class` statement inside the function, followed by `Record.__name__ = Record.__qualname__ = name`,
gives the same result and is easier to read. The standard library already offers both ready
made: `collections.namedtuple(name, fields)` and `dataclasses.make_dataclass(name, fields)` build
classes dynamically, and in real code you would use one of them.

Note that defining `__eq__` without `__hash__` makes the class unhashable (`__hash__` is set to
`None`), just like in a normal class statement. That is correct here, because the records are
mutable.
