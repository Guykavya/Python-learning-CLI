## Approach

`Validator` owns the protocol: it learns its name, stores per instance in
`instance.__dict__[self.name]`, returns itself on class access and turns a missing value into
`AttributeError`. `__set__` calls the hook `self.validate(value)` before storing, so a raise
leaves the old value untouched. `validate` is abstract, which makes `Validator` and any
subclass that forgets it impossible to instantiate. Each concrete validator keeps its settings
in `__init__` and implements only `validate`, using `self.name` in its messages.

## Code

```python
from abc import ABC, abstractmethod


class Validator(ABC):
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError(f"{self.name} has not been set") from None

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self.name] = value

    @abstractmethod
    def validate(self, value):
        """Raise TypeError or ValueError if value is not acceptable."""


class Range(Validator):
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number, got {type(value).__name__}")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}, got {value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} must be <= {self.max_value}, got {value}")


class OneOf(Validator):
    def __init__(self, *options):
        self.options = options

    def validate(self, value):
        if value not in self.options:
            choices = ", ".join(repr(option) for option in self.options)
            raise ValueError(f"{self.name} must be one of {choices}, got {value!r}")


class NonEmptyStr(Validator):
    def __init__(self, max_len=None):
        self.max_len = max_len

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a str, got {type(value).__name__}")
        if not value.strip():
            raise ValueError(f"{self.name} must not be empty")
        if self.max_len is not None and len(value) > self.max_len:
            raise ValueError(f"{self.name} must be at most {self.max_len} characters, got {len(value)}")
```

## Complexity

`Range` and `NonEmptyStr` are O(1) (the `strip` is O(length)); `OneOf` is O(number of
options) because `in` scans the tuple. For many hashable options, store a `frozenset` for O(1)
membership and keep the tuple only for the message.

## Another way

Validators can be **composed** instead of subclassed: one `Field(*checks)` descriptor that
runs a list of small check functions in order.

```python
class Field(Validator):
    def __init__(self, *checks):
        self.checks = checks

    def validate(self, value):
        for check in self.checks:
            check(self.name, value)     # each raises on a bad value
```

That avoids a class per rule but makes the error messages the checks' job. Both designs are
common; libraries such as pydantic and attrs use the composition style.
