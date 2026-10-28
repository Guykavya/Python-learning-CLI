## Approach

`repr(p)` calls `p.__repr__()` (chapter section on repr and str). The method must **return** a string, not print it. Using `!r` on each value keeps strings quoted, so the output looks like valid code.

## Code

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x!r}, {self.y!r})"
```

## Complexity

O(1).

## Another way

Use `type(self).__name__` instead of the literal `Point` so a subclass shows its own name: `f"{type(self).__name__}({self.x!r}, {self.y!r})"`.
