## Approach

The median sits between two halves of the sorted data. We do not need the halves sorted; we need only their **borders**: the largest number of the lower half and the smallest number of the upper half. A max-heap gives the first and a min-heap the second.

- `low`: a max-heap of the smaller half (stored as negatives, because `heapq` is a min-heap). It is allowed to be one item bigger than `high`.
- `high`: a min-heap of the bigger half.

Every `add` keeps two rules: nothing in `low` is bigger than anything in `high`, and `len(low)` is `len(high)` or `len(high) + 1`. The three-step recipe (push to `low`, move the top of `low` to `high`, move one back if `high` became bigger) restores both rules with at most three heap operations. The median is the top of `low` for an odd count and the average of the two tops for an even count.

## Code

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.low = []                                  # max-heap, stored as negatives
        self.high = []                                 # min-heap

    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))      # the largest of low goes up
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))  # rebalance

    def median(self):
        if not self.low:
            raise ValueError("no numbers yet")
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2
```

## Complexity

`add` is `O(log n)` (three heap operations), `median` is `O(1)`, memory `O(n)`.

## Another way

Keep one sorted list and use `bisect.insort` to insert: `median` is `O(1)` by index, but each insertion moves up to `n` items, `O(n)` per `add`. It is fast enough for 100,000 numbers (a memory move is quick) but not for millions. Another way is two heaps plus the opposite rule: first push into the half the number belongs to by comparing with the tops, then rebalance only when the sizes differ by two.
