## Hint 1

For an ascending sort you want the largest item to end at the **end** of the list. If the heap is a **max**-heap, its root is the largest item, and one swap with the last position puts it where it belongs. After the swap, the heap is one item shorter: the item at the end is no longer part of it. What do you have to tell `sift_down` so that it does not touch the sorted part?

## Hint 2

Write `sift_down(i, end)` so that it only looks at children with an index `< end`. Phase 1 calls it with `end = n` for `i` from `n // 2 - 1` down to `0`. Phase 2 loops `end` from `n - 1` down to `1`: swap `a[0]` and `a[end]`, then `sift_down(0, end)`. For `reverse=True` use the same code with the comparison turned around (a min-heap).

## Hint 3

```
n = len(a)
for i from n//2 - 1 down to 0:        # phase 1
    sift_down(i, n)
for end from n - 1 down to 1:         # phase 2
    swap a[0] and a[end]
    sift_down(0, end)                 # the heap is a[:end]
sift_down(i, end): like the sift_down of the earlier problem, but
    pick the LARGER child (ascending) or the SMALLER child (reverse), and look only at indexes < end
```
