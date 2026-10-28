## Approach

The dict needs `hash` to pick the bucket and `==` to confirm. Both must use the **same** normalised value, otherwise equal keys land in different buckets.

## Code

```python
class HeaderName:
    def __init__(self, text):
        self.text = text
        self._key = text.casefold()

    def __eq__(self, other):
        if not isinstance(other, HeaderName):
            return NotImplemented
        return self._key == other._key

    def __hash__(self):
        return hash(self._key)

    def __repr__(self):
        return f"HeaderName({self.text!r})"

    def __str__(self):
        return self.text
```

## Complexity

O(len(text)) to build the key, O(1) afterwards.

## Another way

Subclass `str` and override `__eq__`/`__hash__`; it gives you string methods for free, but it is easier to get subtly wrong.
