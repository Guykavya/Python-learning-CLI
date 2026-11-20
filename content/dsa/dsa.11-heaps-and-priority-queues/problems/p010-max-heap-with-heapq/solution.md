## Approach

A min-heap of the negated numbers is a max-heap of the numbers: `-a < -b` exactly when `a > b`, so the smallest stored value belongs to the largest real value. The class hides this: it negates on the way in (`__init__`, `push`) and again on the way out (`pop`, `peek`).

## Code

```python
import heapq


class MaxHeap:
    def __init__(self, items=()):
        self._h = [-x for x in items]
        heapq.heapify(self._h)

    def push(self, x):
        heapq.heappush(self._h, -x)

    def pop(self):
        return -heapq.heappop(self._h)

    def peek(self):
        return -self._h[0]

    def __len__(self):
        return len(self._h)
```

## Complexity

`push`, `pop`: `O(log n)`. `peek`, `len`: `O(1)`. Build: `O(n)`.

## Another way

For items that cannot be negated (strings, tuples, objects), wrap each item in a small class whose `__lt__` is reversed (chapter section 5, class `Reversed`), or store tuples with a negated numeric key: `(-priority, counter, item)`. On Python 3.14 and later you can also use `heapq.heappush_max`; code that must run on older versions uses negation.
