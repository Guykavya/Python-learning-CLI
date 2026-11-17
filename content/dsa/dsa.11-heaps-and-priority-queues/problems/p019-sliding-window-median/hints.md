## Hint 1

Start from the running median (two heaps, lower half in a max-heap, upper half in a min-heap). With a sliding window the only new thing is that a number **leaves**. Removing an item from the middle of a heap is expensive. What if you do not remove it, but only *mark* it as gone and throw it away when it reaches the top?

## Hint 2

To mark a number as gone you must know **which one** it is, even when the same value appears several times. Store each heap entry together with its **index** in `nums`: `(-value, index)` in the lower heap and `(value, index)` in the upper heap. Keep a list `side` with one entry per index, telling where the number lives now: in `low`, in `high`, or nowhere. A heap entry whose `side` does not match its heap is stale: pop it when it reaches the top.

Also keep two counters, `lo_n` and `hi_n`, the number of **live** entries in each heap. The sizes of the halves are about live numbers, not about `len(heap)`.

## Hint 3

```
side = [nowhere] * n
for i, x in enumerate(nums):
    prune both heaps                        # throw away stale tops
    if low is not empty and x > top of low: push (x, i) into high, side[i] = high, hi_n += 1
    else:                                  push (-x, i) into low,  side[i] = low,  lo_n += 1
    if i >= k:                             # nums[i - k] leaves
        decrement the counter of the side it lives on; side[i - k] = nowhere
    while lo_n > hi_n + 1: prune; move the top of low to high (update side and counters)
    while lo_n < hi_n:     prune; move the top of high to low
    if i >= k - 1:
        prune
        k odd: the top of low;  k even: the average of the two tops
```
