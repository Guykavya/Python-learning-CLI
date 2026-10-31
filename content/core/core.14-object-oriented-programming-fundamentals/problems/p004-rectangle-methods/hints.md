## Hint 1

`area`, `perimeter` and `is_square` only read `self.width` and `self.height`. `scale` must write
new values into them. Which statement changes an attribute of the object: `width = width * 2` or
`self.width = self.width * 2`?

## Hint 2

```
def scale(self, factor):
    if factor <= 0: raise ValueError("factor must be positive")
    self.width = self.width * factor
    self.height = self.height * factor
    # no return statement -> the method returns None
```

For `is_square`, `self.width == self.height` is already `True` or `False`; you can return it
directly.
