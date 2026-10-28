## Hint 1

Why does `"1.10.0" < "1.2.0"` give the wrong answer? What should you compare instead, and how do you get there from the text?

## Hint 2

Split on `"."`, check there are exactly 3 parts and each `isdigit()`, then turn them into ints. Keep them as one tuple `self._key`; use that tuple in `__eq__`, `__lt__` and `__hash__`.

## Hint 3

```
@total_ordering
class Version:
    __init__: parts = text.split(".") ; need 3 digit-only parts else ValueError
              self.major, self.minor, self.patch = ints ; self._key = (major, minor, patch)
    __eq__ / __lt__ : NotImplemented for non-Version ; compare _key
    __hash__ : hash(self._key)
    __str__ : "major.minor.patch" ; __repr__ : Version('...')
```
