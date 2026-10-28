## Approach

Every method gets the rectangle as `self` (chapter section 3). The reading methods compute their
answer from `self.width` and `self.height` **each time they are called**, so they always match the
current size. `scale` assigns new values to the same two attributes; that is what "in place" means.
It has no `return`, so it returns `None`, the same convention as `list.sort()` or `list.append()`.

Compare with `Point.moved` in p001, which returned a new object and left the old one alone. Both
designs are fine; the important thing is to make it obvious which one a method uses.

## Code

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def is_square(self):
        return self.width == self.height

    def scale(self, factor):
        if factor <= 0:
            raise ValueError("factor must be positive")
        self.width = self.width * factor
        self.height = self.height * factor
```

## Complexity

O(1) for every method.

## Another way

A non-mutating version, `scaled(factor)`, would `return Rectangle(self.width * factor, self.height * factor)`.
Python's naming habit shows the difference: `list.sort()` changes in place, `sorted(list)` returns a
new list. In section 8 you will see `area` written as a *property*, so you can write `r.area`
without brackets.
