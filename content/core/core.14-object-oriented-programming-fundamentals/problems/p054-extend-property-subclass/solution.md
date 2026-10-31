## Approach

A property is an object stored on the class (chapter section 8). When `BoundedValue` defines a new
`value`, it replaces the parent's property for its instances, because attribute lookup finds it first
in the MRO. To keep the parent's rules we do not copy them; we **call** the parent's setter function,
`Value.value.fset`.

`@Value.value.setter` is the neat way to write the override: it copies `Value`'s property with the
same getter and our new setter, and stores it under the name `value` in `BoundedValue`.

One ordering detail matters: `Value.__init__` assigns `self.value`, which already runs
**`BoundedValue`'s** setter (the object is a `BoundedValue`). That setter reads `self.upper`, so
`upper` must be stored **before** calling `super().__init__`.

## Code

```python
def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


class Value:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        if not _is_number(new):
            raise TypeError("value must be a number")
        if new < 0:
            raise ValueError("value must be >= 0")
        self._value = new


class BoundedValue(Value):
    def __init__(self, value, upper):
        if not _is_number(upper) or upper < 0:
            raise ValueError("upper must be a number >= 0")
        self.upper = upper  # must exist before the setter runs
        super().__init__(value)

    @Value.value.setter
    def value(self, new):
        if _is_number(new) and new > self.upper:
            raise ValueError(f"value must be <= {self.upper}")
        Value.value.fset(self, new)
```

`_is_number` is a small module-level helper. `isinstance(True, int)` is `True`, so `bool` must be
excluded on purpose.

## Complexity

O(1) per assignment.

## Another way

Template method (chapter section 10): give `Value` a method `check(self, new)` that the setter calls
before storing. `BoundedValue` then overrides only `check`, calls `super().check(new)` and adds its
rule; the property itself is not touched in the subclass. This is often cleaner when several subclasses
add rules, and it lets you use normal `super()`.
