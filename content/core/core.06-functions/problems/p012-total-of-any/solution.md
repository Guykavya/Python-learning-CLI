## Approach

`*numbers` collects every positional argument into a tuple, possibly empty. Loop over it with a
running total that starts at 0, so the empty case needs no special handling.

## Code

```python
def total(*numbers):
    """Return the sum of all the numbers passed in (0 if none)."""
    result = 0
    for n in numbers:
        result += n
    return result
```

## Complexity

O(n) for n arguments.

## Another way

`return sum(numbers)`: the built-in accepts the tuple directly. This exercise forbids it only so
you see that `numbers` is an ordinary tuple you can loop over.
