## Hint 1

If two keys are equal, which other method must agree with `__eq__` so that a dict finds the same slot? Which string method turns "Content-Type" and "CONTENT-TYPE" into the same text?

## Hint 2

Compute the normalised text once in `__init__` (`self._key = text.casefold()`), then use `_key` in both `__eq__` and `__hash__`.

## Hint 3

```
__init__: self.text = text ; self._key = text.casefold()
__eq__:   not a HeaderName -> NotImplemented ; else compare _key
__hash__: hash(self._key)
__repr__: HeaderName(<text!r>) ;  __str__: text
```
