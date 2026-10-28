## Approach

Parse the spec in two small steps (unit, then precision), validating as you go. Convert the stored Celsius value, then format with a nested precision `{value:.{digits}f}`.

## Code

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __repr__(self):
        return f"Temperature({self.celsius!r})"

    def __format__(self, spec):
        unit = "C"
        digits = 1
        if spec and spec[-1].isalpha():
            unit = spec[-1]
            spec = spec[:-1]
        if unit not in ("C", "F", "K"):
            raise ValueError(f"unknown unit: {unit}")
        if spec:
            if not spec.startswith(".") or not spec[1:].isdigit():
                raise ValueError(f"bad precision: {spec}")
            digits = int(spec[1:])
        if unit == "F":
            value = self.celsius * 9 / 5 + 32
        elif unit == "K":
            value = self.celsius + 273.15
        else:
            value = self.celsius
        return f"{value:.{digits}f} {unit}"
```

## Complexity

O(len(spec)), effectively constant.

## Another way

A regular expression `^(?:\.(\d+))?([CFK])?$` parses the whole spec in one step; the manual way is easier to read and debug.
