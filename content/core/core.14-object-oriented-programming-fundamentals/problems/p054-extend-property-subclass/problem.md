# Extend a validated property in a subclass

A property is a class attribute, so a subclass can override it like a method. The tricky part is to
**add** a rule to the setter while **reusing** the parent's checks, instead of copying them.

In `solution.py` write two classes.

### `Value`

- `Value(value)`: stores the number through the property (so the checks run in `__init__` too).
- Property `value`, stored in the attribute `self._value`. The setter checks, in this order:
  1. `new` must be an `int` or a `float`, and not a `bool`; otherwise
     `TypeError("value must be a number")`.
  2. `new` must be `>= 0`; otherwise `ValueError("value must be >= 0")`.

### `BoundedValue(Value)`

- `BoundedValue(value, upper)`: `upper` must be a number `>= 0` (same type rule), otherwise
  `ValueError("upper must be a number >= 0")`. Store it as `self.upper` and then let `Value.__init__`
  store the value.
- It **overrides** the `value` property. The getter is the same as in `Value`. The setter:
  1. if `new` is an `int` or `float` (not a `bool`) and `new > self.upper`, raise
     `ValueError(f"value must be <= {self.upper}")`;
  2. otherwise it hands `new` to the **setter of `Value`**, which does the type check, the `>= 0`
     check and stores it. Do not copy those checks into `BoundedValue`.
- A failed assignment leaves the old value unchanged.

Useful facts: `Value.value` is the property object. `Value.value.fset` is its setter function, and
`Value.value.fset(self, new)` calls it. `@Value.value.setter` creates a **new** property that keeps
`Value`'s getter and uses your new setter. (Note: `super().value = new` does **not** work: `super()`
can read attributes but cannot assign them.)

## Example

```python
v = Value(5)
v.value = 2.5          # fine
v.value = -1           # ValueError: value must be >= 0
v.value = "7"          # TypeError: value must be a number

b = BoundedValue(5, upper=10)
b.value                # 5
b.value = 10           # fine, the limit is inclusive
b.value = 11           # ValueError: value must be <= 10
b.value = -3           # ValueError: value must be >= 0   (from Value's setter)
b.value                # 10   (failed assignments changed nothing)
BoundedValue(20, 10)   # ValueError: value must be <= 10  (the check runs in __init__ too)
BoundedValue(1, -5)    # ValueError: upper must be a number >= 0
```
