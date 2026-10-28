## Hint 1

First peel off the unit: if the spec is not empty and its last character is a letter, that letter is the unit and the rest is the precision part. What do you do with an unknown letter?

## Hint 2

The precision part, if not empty, must look like `.` followed by digits. Check `rest.startswith('.')` and `rest[1:].isdigit()`. Then build the number with `f"{value:.{p}f}"`.

## Hint 3

```
def __format__(self, spec):
    unit = "C"; digits = 1
    if spec and spec[-1].isalpha():
        unit = spec[-1]; spec = spec[:-1]
    if unit not in "CFK": raise ValueError
    if spec:
        if not (spec starts with "." and the rest is digits): raise ValueError
        digits = int(spec[1:])
    value = convert(self.celsius, unit)
    return f"{value:.{digits}f} {unit}"
```
