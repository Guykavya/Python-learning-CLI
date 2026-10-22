## Approach

`iter(read, '')` builds an iterator that calls `read()` for each `next()`. The first time `read()` returns `''` it raises `StopIteration` and the `''` is not yielded. `list(...)` collects the rest.

## Code

```python
def read_chunks(read):
    return list(iter(read, ""))
```

## Complexity

O(n) calls to `read`.

## Another way

A `while True` loop with `chunk = read(); if chunk == '': break` does the same, but `iter(read, '')` can be handed to `for`, `map`, `sum` and everything else that takes an iterable.
