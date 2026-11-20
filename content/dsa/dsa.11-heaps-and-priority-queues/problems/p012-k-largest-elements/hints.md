## Hint 1

You want to keep the `k` best items, and when a better one arrives, you must throw away the **worst of the kept ones**. Which of the kept items is the worst? Which kind of heap gives you the smallest item in `O(1)`? So which kind do you need, and what is `heap[0]`?

## Hint 2

Loop over `nums`. While the heap has fewer than `k` items, `heappush`. After that, compare `x` with `heap[0]`: if `x` is bigger, `heapreplace(heap, x)` (it pops the root and pushes `x` in one step); if not, skip `x`. Do the `k <= 0` check first, because `heap[0]` on an empty heap is an `IndexError`. At the end, `heappop` gives the kept items smallest first.

## Hint 3

```
if k <= 0: return []
heap = []
for x in nums:
    if len(heap) < k:   heappush(heap, x)
    elif x > heap[0]:   heapreplace(heap, x)
result = [heappop(heap) for _ in range(len(heap))]      # smallest first
result.reverse()                                         # largest first
return result
```
