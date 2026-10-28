## Hint 1

A property has a getter (`@property def celsius(self)`) and a setter (`@celsius.setter`). Where
does the real number live? If the getter returned `self.celsius`, what would happen when you read
it? Why does the backing attribute need a different name, like `_celsius`?

## Hint 2

In `__init__`, write `self.celsius = celsius` (no underscore). That line goes **through** the setter,
so the check runs for new objects too. The `fahrenheit` setter can also just assign
`self.celsius = ...`, and the celsius setter does the check for it.

## Hint 3

```
class Temperature:
    def __init__(self, celsius=0):
        self.celsius = celsius              # uses the setter

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15: raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9
```
