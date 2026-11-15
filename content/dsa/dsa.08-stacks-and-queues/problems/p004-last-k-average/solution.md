## Approach

The window holds the last `k` values; `maxlen=k` makes the deque forget the oldest one on its own. A running `total` keeps the sum of the window, so each average costs `O(1)`: subtract the value that is about to leave (the front, `window[0]`), append the new value, add it.

## Code

```python
from collections import deque


def moving_averages(values, k):
    window = deque(maxlen=k)
    total = 0
    out = []
    for x in values:
        if len(window) == k:
            total -= window[0]          # the value that append is about to drop
        window.append(x)
        total += x
        out.append(total / len(window))
    return out
```

## Complexity

`O(n)` time for `n` values (each step is `O(1)`), `O(k)` memory for the window. Calling `sum(window)` each time would be `O(n * k)`: 5 * 10**9 additions for the big test.

## Another way

Without a deque you can use the list itself: the value leaving the window at position `i` is `values[i - k]`.

```python
def moving_averages(values, k):
    total, out = 0, []
    for i, x in enumerate(values):
        total += x
        if i >= k:
            total -= values[i - k]
        out.append(total / min(i + 1, k))
    return out
```

This works only when all values are available up front. The deque version also works for a stream that arrives one value at a time.
