## Hint 1

You never need the numbers that are **not** among the `k` largest seen so far: they can never be the k-th largest later, because the `k` bigger ones will stay bigger. So keep only `k` numbers. Which of those `k` is the answer, the biggest or the smallest? And which kind of heap gives you that one in `O(1)`?

## Hint 2

Keep a **min**-heap with at most `k` items. Its root is the smallest of the `k` largest, which is exactly the k-th largest. In `add(val)`: if the heap has fewer than `k` items, push `val`; otherwise, if `val` is larger than the root, replace the root with `val`; otherwise ignore it. The constructor can simply call `add` for every number in `nums`.

## Hint 3

```
__init__(k, nums):  self.k = k;  self.heap = [];  for x in nums: self.add(x)
add(val):
    if len(heap) < k:          heappush(heap, val)
    elif val > heap[0]:        heapreplace(heap, val)
    if len(heap) == k:  return heap[0]
    else:               return None            # fewer than k numbers seen
```
