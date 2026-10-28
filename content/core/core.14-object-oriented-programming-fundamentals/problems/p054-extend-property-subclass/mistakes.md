- Writing `super().value = new`. `super()` objects support reading attributes, not assigning them:
  `AttributeError`.
- Setting `self.upper` **after** `super().__init__(value)`. The subclass setter runs inside
  `Value.__init__` and finds no `upper` yet.
- Copying the type and `>= 0` checks into `BoundedValue`. Two copies of a rule drift apart; reuse
  `Value.value.fset(self, new)`.
- Defining only a new setter with `@property` missing. A plain `def value(self, new)` in the subclass
  replaces the property with a method, and `b.value` returns a bound method.
- Writing `self.value = new` inside the subclass setter to "pass it on". That calls the same setter
  again and again: `RecursionError`.
- Comparing `new > self.upper` before checking the type. `"7" > 10` raises a `TypeError` with
  Python's own message, not `value must be a number`.
