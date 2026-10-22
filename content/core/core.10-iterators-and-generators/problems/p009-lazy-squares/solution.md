## Approach

A generator expression `(expr for x in xs)` makes a generator object right away without running the loop. The first `next` runs the loop until it has one value.

## Code

```python
def lazy_squares(numbers):
    return (n * n for n in numbers)
```

## Complexity

O(1) memory regardless of the size of `numbers`. Total time O(n) when fully consumed.

## Another way

A small generator function with `for n in numbers: yield n * n` is identical in behaviour.
