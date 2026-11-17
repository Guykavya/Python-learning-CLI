## Hint 1

Run the starter by hand on `[3, 1, 5, 12, 2, 11, 7]` with `k = 3`. The heap stores `-3, -1, -5`. Which stored number is `heap[0]`? Is it the best or the worst score of the three? Then `12` arrives: is `-12 > heap[0]`? And `2`: is `-2 > heap[0]`? Which scores end up kept?

## Hint 2

A heap of negated scores has the **best** kept score at the root, because the smallest negative number is the largest score. The code replaces the root when a new score is "better", so it throws away the best kept score and keeps the **worst** ones: it returns the `k` lowest scores. To throw away the **worst** kept score, the root must be the worst, the smallest score. Which heap has the smallest item at the root without any negation?

The crash: with `k = 0` the heap stays empty (`len(heap) < 0` is false), and the first `heap[0]` raises `IndexError`. What must the function do before the loop?

## Hint 3

```
if k <= 0: return []
heap = []                                  # a MIN-heap of the scores themselves
for s in scores:
    if len(heap) < k:      heappush(heap, s)
    elif s > heap[0]:      heapreplace(heap, s)      # better than the weakest kept score
return sorted(heap, reverse=True)
```
