## Approach

`slice` objects arrive as one argument. Let the stored list do the real slicing, then wrap the result so the caller gets the same kind of object back. Using `type(self)(...)` instead of `Sentence(...)` keeps subclasses working.

## Code

```python
class Sentence:
    def __init__(self, words):
        self._words = list(words)

    def __repr__(self):
        return f"Sentence({self._words!r})"

    def __len__(self):
        return len(self._words)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(self._words[key])
        if isinstance(key, int):
            return self._words[key]
        raise TypeError("indices must be integers or slices")

    def __str__(self):
        return " ".join(self._words)
```

## Complexity

O(k) for a slice of k items, O(1) for an index.

## Another way

Return the list from a slice (simple, but then `s[1:3][0]` works while `s[1:3].some_method()` does not); real code often prefers returning the same type.
