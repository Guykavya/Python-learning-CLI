## Hint 1

`BoundedValue.__init__` calls `super().__init__(value)`, and that runs `self.value = value`. Which
setter runs there: `Value`'s or `BoundedValue`'s? What attribute does `BoundedValue`'s setter need at
that moment, and has it been set yet?

## Hint 2

You cannot write `super().value = new`. But the parent's property object is just a class attribute:
`Value.value`. Its setter function is `Value.value.fset`, a normal function that takes `(self, new)`.
And `@Value.value.setter` builds a new property with `Value`'s getter plus your setter.

## Hint 3

```text
class BoundedValue(Value):
    __init__(self, value, upper):
        if upper is not a number or upper < 0: ValueError(...)
        self.upper = upper            # BEFORE super().__init__
        super().__init__(value)

    @Value.value.setter
    def value(self, new):
        if new is a number and new > self.upper: ValueError(f"value must be <= {self.upper}")
        Value.value.fset(self, new)   # type check, >= 0, store
```
