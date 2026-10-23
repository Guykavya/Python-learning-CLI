## Approach

`pairwise` reads the input once and yields consecutive pairs. A list with fewer than two items gives no pairs, so the result is empty with no special case.

## Code

```python
from itertools import pairwise


def differences(numbers):
    return [b - a for a, b in pairwise(numbers)]
```

## Complexity

O(n).

## Another way

`[numbers[i + 1] - numbers[i] for i in range(len(numbers) - 1)]` works for lists only. The `pairwise` version also works for generators.
