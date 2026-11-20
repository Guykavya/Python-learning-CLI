## Approach

The k-th largest of a growing set only depends on its `k` largest members. A min-heap of exactly those `k` numbers has the k-th largest at its root. A new number either is too small to matter (it is not larger than the root) or it pushes the root out. The constructor reuses `add`, so the numbers in `nums` are treated like the first numbers of the stream. Until the heap holds `k` numbers, the answer does not exist and `add` returns `None`.

## Code

```python
import heapq


class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = []
        for x in nums:
            self.add(x)

    def add(self, val):
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, val)
        elif val > self.heap[0]:
            heapq.heapreplace(self.heap, val)
        return self.heap[0] if len(self.heap) == self.k else None
```

## Complexity

`add`: `O(log k)` time (one comparison if `val` is too small). Memory `O(k)`. The constructor: `O(n log k)` for `n` initial numbers.

## Another way

Push every number and pop when the heap has more than `k` items: `heappush(h, val)` then `if len(h) > k: heappop(h)`. It is shorter and correct; each `add` pays a push and a pop even for numbers that cannot matter (the tests allow it: about 4 comparisons per add for `k = 5`). `heapq.heappushpop(h, val)` does the push-then-pop in one call and returns at once when `val` is not larger than the root. Sorting all numbers at every `add` is `O(n log n)` per call and `O(n)` memory: it is the version the tests reject.
