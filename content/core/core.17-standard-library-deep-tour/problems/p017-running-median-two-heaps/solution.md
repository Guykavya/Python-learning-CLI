## Approach

Split the numbers seen so far into a lower half and an upper half.

- `low` is a max-heap (values stored negated): `-low[0]` is the largest of the small numbers.
- `high` is a min-heap: `high[0]` is the smallest of the big numbers.

If `low` always has the same number of items as `high`, or one more, the median sits on the
tops: `-low[0]` for an odd count, the average of the two tops for an even count.

`add(x)`:
1. Put `x` in the right half: into `low` if it is `<=` the top of `low` (or `low` is empty),
   otherwise into `high`. This keeps "everything in low <= everything in high".
2. Rebalance: if `low` has two more than `high`, move `low`'s top to `high`; if `high` has more than
   `low`, move `high`'s top to `low`. Moving a **top** never breaks the ordering rule, because it is
   the item closest to the border.

Each step is a constant number of heap pushes and pops: O(log n).

## Code

```python
import heapq
from collections.abc import Iterable


class MedianKeeper:
    def __init__(self) -> None:
        self._low: list[float] = []   # max-heap of the smaller half, values negated
        self._high: list[float] = []  # min-heap of the larger half

    def add(self, x: float) -> None:
        if not self._low or x <= -self._low[0]:
            heapq.heappush(self._low, -x)
        else:
            heapq.heappush(self._high, x)
        if len(self._low) > len(self._high) + 1:
            heapq.heappush(self._high, -heapq.heappop(self._low))
        elif len(self._high) > len(self._low):
            heapq.heappush(self._low, -heapq.heappop(self._high))

    def median(self) -> float:
        if not self._low:
            raise ValueError("median of an empty MedianKeeper")
        if len(self._low) > len(self._high):
            return -self._low[0]
        return (-self._low[0] + self._high[0]) / 2

    def __len__(self) -> int:
        return len(self._low) + len(self._high)


def running_medians(nums: Iterable[float]) -> list[float]:
    keeper = MedianKeeper()
    result = []
    for x in nums:
        keeper.add(x)
        result.append(keeper.median())
    return result
```

## Complexity

`add`: O(log n). `median`: O(1). Memory O(n): every number must be kept, because any of them can
become the median later.

## Another way

A popular variant always pushes into `low`, then moves `low`'s top to `high`, then moves `high`'s
top back if `high` became bigger. It is shorter, with no comparison, but does up to three heap
operations per number. Keeping a sorted list with `bisect.insort` is O(n) per number because of
the list shifting, and `statistics.median(history)` re-sorts everything: O(n log n) per number.
Both are fine for a few thousand numbers and far too slow for a real stream.
