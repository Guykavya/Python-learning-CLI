## Approach

Walk the input once. Keep a tuple `window` with the most recent items. Add each new item at
the end. If the tuple is now longer than `k`, drop its first item. Whenever it has exactly
`k` items, yield it.

Tuples cannot change, so every window we yield is a separate object. The caller can keep them.

## Code

```python
def windows(iterable, k):
    window = ()
    for item in iterable:
        window = window + (item,)
        if len(window) > k:
            window = window[1:]
        if len(window) == k:
            yield window
```

## Complexity

O(n * k) time, because each `window + (item,)` copies `k` items. Memory is O(k).
For small `k` (like 3 or 7) this is fast.

## Another way

`collections.deque(maxlen=k)` drops the oldest item by itself when you append:

```python
from collections import deque

def windows(iterable, k):
    window = deque(maxlen=k)
    for item in iterable:
        window.append(item)
        if len(window) == k:
            yield tuple(window)
```

For `k == 2`, Python 3.10+ has `itertools.pairwise`.
