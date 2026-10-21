## Approach

`reduce` folds the list: it starts the accumulator at the initial value `1`, then multiplies it by
each item in turn. `1` is the identity for multiplication, so it does not change any product and
it is the right answer for an empty list.

## Code

```python
from functools import reduce


def product(numbers):
    """Return the product of numbers (1 for an empty list), using reduce."""
    return reduce(lambda acc, n: acc * n, numbers, 1)
```

## Complexity

O(n) multiplications.

## Another way

`math.prod(numbers)` is the built-in way and also returns 1 for an empty list.
