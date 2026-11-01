## Approach

The adapter **holds** the legacy object (composition) and translates: it calls the old method,
parses the text, converts the unit and exposes the new interface (`celsius()`). The new code
(`monitor`) never learns that a legacy class exists, and the legacy class stays untouched.
Python's duck typing means the adapter needs no base class or registration.

## Code

```python
from types import SimpleNamespace


def _to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


class FahrenheitAdapter:
    def __init__(self, legacy):
        self._legacy = legacy

    def celsius(self):
        text = self._legacy.read_fahrenheit_string().strip()
        return _to_celsius(float(text.rstrip("Ff")))


def adapt_function(read_f):
    return SimpleNamespace(celsius=lambda: _to_celsius(read_f()))
```

(`LegacyTemperatureSensor` and `monitor` stay as given.)

## Complexity

O(1) per call (parsing a short string).

## Another way

`adapt_function` can be reused for the class adapter: the legacy reading is just a function
that returns a float.

```python
def FahrenheitAdapter(legacy):
    return adapt_function(lambda: float(legacy.read_fahrenheit_string().strip().rstrip("Ff")))
```

Subclassing the legacy class would also "work" but couples you to its internals; a wrapper
survives vendor changes better. Monkeypatching (`LegacyTemperatureSensor.celsius = ...`) is a
trap: it changes the class for every other user in the same process.
