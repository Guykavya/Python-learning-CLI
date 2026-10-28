## Approach

A property looks like an attribute to the user but runs a method (chapter section 8). The real
number lives in a backing attribute with a different name, `_celsius`; the underscore says "internal,
please use the property" (section 7). The getter cannot return `self.celsius`: that would call the
getter again, forever (`RecursionError`).

Two small tricks make the class short and safe:

1. `__init__` assigns `self.celsius = celsius`, **without** the underscore. That goes through the
   setter, so a new object is checked exactly like a later change.
2. The `fahrenheit` setter converts and assigns `self.celsius = ...`, so the one check in the celsius
   setter protects both ways in. Fahrenheit is never stored; it is computed when read, so it can never
   disagree with celsius.

## Code

```python
ABSOLUTE_ZERO = -273.15


class Temperature:
    def __init__(self, celsius=0):
        self.celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < ABSOLUTE_ZERO:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9
```

## Complexity

O(1) for every read and write.

## Another way

You could also write `get_celsius()` / `set_celsius(v)` methods, as in Java. Python prefers to start
with a plain attribute and switch to a property later, when a rule is needed: the code that uses the
class (`t.celsius = 30`) does not have to change at all.
