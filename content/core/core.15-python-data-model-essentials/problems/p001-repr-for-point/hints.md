## Hint 1

How does Python turn an object into text when you call `repr(p)`? It calls `p.__repr__()`. What must that method return: a string or a print?

## Hint 2

The `repr` of the *values* matters: `repr('a')` is `"'a'"` (with quotes), while `str('a')` is `a`. In an f-string, `{value!r}` calls `repr` on the value.

## Hint 3

```
class Point:
    __init__: store x, y
    __repr__(self):
        return "Point(" + repr(self.x) + ", " + repr(self.y) + ")"   # or an f-string with !r
```
