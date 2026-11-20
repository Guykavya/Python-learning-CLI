## Approach

A min-heap of size `k` always holds the `k` largest items seen so far, and its root is the weakest of them, the one that must leave when a better item arrives. Most items in a random input are weaker than the root and cost one comparison; only the few that beat the root cause a `heapreplace` of `O(log k)`. At the end the pops give the kept items from smallest to largest, so reversing the list gives the answer largest first.

## Code

```python
import heapq


def k_largest(nums, k):
    if k <= 0:
        return []
    heap = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    result = [heapq.heappop(heap) for _ in range(len(heap))]
    result.reverse()
    return result
```

## Complexity

`O(n log k)` time (about `n` plus `k ln(n / k) log k` for random input), `O(k)` memory. `n` pushes and pops on a heap of **all** items would be `O(n log n)`.

## Another way

`heapq.nlargest(k, nums)` is exactly this algorithm, ready made. Sorting everything and slicing is simplest (`sorted(nums, reverse=True)[:k]`), but `O(n log n)` time and `O(n)` memory, and it cannot work on a stream. `heapq.heappushpop(heap, x)` pushes `x` and pops the smallest in one call, and it returns `x` at once when `x` is not larger than the root: `if len(heap) < k: heappush(heap, x) else: heappushpop(heap, x)` does the same work with fewer lines. Quickselect finds the `k`-th largest in `O(n)` on average.
