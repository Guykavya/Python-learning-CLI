## Approach

`format(x, spec)` calls `type(x).__format__(x, spec)`. Your method is a small `if` chain on the spec. The default `object.__format__` rejects any non-empty spec, which is why the starter fails.

## Code

```python
class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"

    def __format__(self, spec):
        if spec == "":
            return str(self)
        if spec == "hex":
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
        if spec == "rgb":
            return f"rgb({self.r}, {self.g}, {self.b})"
        raise ValueError(f"unknown format spec: {spec}")
```

## Complexity

O(1).

## Another way

Use a dict of spec to function, `{"hex": ..., "rgb": ...}`, and look the spec up. For numbers, delegate unknown specs to the built-in with `format(self.value, spec)`.
