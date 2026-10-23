## Approach

`cycle` remembers the items of the first pass and replays them. `islice` cuts the endless stream to length `n`.

## Code

```python
from itertools import cycle, islice


def cycle_labels(labels, n):
    return list(islice(cycle(labels), n))
```

## Complexity

O(n) time; `cycle` stores one copy of `labels`.

## Another way

`[labels[i % len(labels)] for i in range(n)]` works for lists but fails for empty `labels` (division by zero) and does not work for iterators.
