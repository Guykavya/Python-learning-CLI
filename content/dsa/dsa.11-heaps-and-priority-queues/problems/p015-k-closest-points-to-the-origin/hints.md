## Hint 1

You need the `k` points with the smallest squared distance. While you scan the points you keep the `k` best so far. When a new point is closer than the **worst** of the kept ones, the worst one leaves. Which kept point is the worst, and how can a min-heap give it to you in `O(1)`? Think of storing the **negative** of the distance.

## Hint 2

The final order is by `(d, x, y)`, where `d = x*x + y*y`. The point to throw away is the one with the **largest** `(d, x, y)`. A min-heap gives the smallest stored tuple, so store the key with every part negated: `(-d, -x, -y)`. The smallest stored tuple is then the largest `(d, x, y)`: the root is exactly the point to replace. A new point must replace the root when its stored tuple is **larger** than the root (that means its `(d, x, y)` is smaller). Comparing the whole tuple also decides the ties at the border correctly.

## Hint 3

```
if k <= 0: return []
heap = []
for (x, y) in points:
    entry = (-(x*x + y*y), -x, -y)
    if len(heap) < k:       heappush(heap, entry)
    elif entry > heap[0]:   heapreplace(heap, entry)
best = sorted((-nd, -nx, -ny) for nd, nx, ny in heap)      # back to (d, x, y), nearest first
return [(x, y) for d, x, y in best]
```
