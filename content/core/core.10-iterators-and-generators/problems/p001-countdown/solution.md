## Approach

A generator function is a normal-looking function with `yield` in it. Calling it builds a generator object without running any body code. Each `next()` runs the body until the next `yield`. When the body ends, `StopIteration` is raised automatically.

## Code

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1
```

## Complexity

O(n) time to produce all values, O(1) extra memory: only the current number is kept.

## Another way

`yield from range(n, 0, -1)` does the same in one line, and `range` is itself a lazy sequence.
