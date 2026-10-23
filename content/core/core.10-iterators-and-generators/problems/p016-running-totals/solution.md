## Approach

`accumulate` yields the first item, then `func(first, second)`, then `func(that, third)`, and so on. The default function is addition.

## Code

```python
from itertools import accumulate


def running_totals(numbers):
    return list(accumulate(numbers))


def running_max(numbers):
    return list(accumulate(numbers, max))
```

## Complexity

O(n) time and memory.

## Another way

A `for` loop with a `total` variable and `append` works and is just as fast. `accumulate` says what you mean in one line.
