## Approach

Loop over the items, call `func` on each, and append the result to a new list. This is what `map` does, except that `map` is lazy and returns an iterator.

## Code

```python
def apply_to_all(func, items):
    """Return a new list of func(item) for each item."""
    result = []
    for item in items:
        result.append(func(item))
    return result
```

## Complexity

O(n) calls of `func`.

## Another way

`return [func(item) for item in items]` is the comprehension version, and `list(map(func, items))` the built-in one.
