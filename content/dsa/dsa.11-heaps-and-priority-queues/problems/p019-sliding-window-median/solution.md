## Approach

Take the two-heap running median and add **lazy deletion**. A number that leaves the window is not removed from its heap; it is only marked as gone. Every heap entry carries its index in `nums`, so "which number leaves" is exact even with duplicate values. The list `side[i]` says where the number `i` lives (`0` = lower half, `1` = upper half, `2` = nowhere). An entry is **stale** when `side` of its index does not match its heap. Before the tops are used, stale tops are popped (`prune`).

The balance is about the **live** counts `lo_n` and `hi_n`, which we maintain by hand, because `len(heap)` also counts stale entries. After each step we keep `lo_n == hi_n` or `lo_n == hi_n + 1`, moving the top of one heap to the other when needed. For a full window the median is the top of the lower half (`k` odd) or the average of the two tops (`k` even).

The rule for a new number, "into `high` when it is bigger than the top of `low`, otherwise into `low`", keeps every live number of `low` at most every live number of `high`.

## Code

```python
import heapq

def sliding_median(nums, k):
    n = len(nums)
    if k < 1 or k > n:
        return []
    low, high = [], []                 # low: (-value, index), high: (value, index)
    side = [2] * n                     # 0 = live in low, 1 = live in high, 2 = nowhere
    lo_n = hi_n = 0                    # live entries in each heap

    def prune():
        while low and side[low[0][1]] != 0:
            heapq.heappop(low)
        while high and side[high[0][1]] != 1:
            heapq.heappop(high)

    out = []
    for i, x in enumerate(nums):
        prune()
        if low and x > -low[0][0]:
            heapq.heappush(high, (x, i)); side[i] = 1; hi_n += 1
        else:
            heapq.heappush(low, (-x, i)); side[i] = 0; lo_n += 1
        if i >= k:                     # nums[i - k] leaves the window
            j = i - k
            if side[j] == 0:
                lo_n -= 1
            else:
                hi_n -= 1
            side[j] = 2
        while lo_n > hi_n + 1:
            prune()
            value, j = heapq.heappop(low)
            heapq.heappush(high, (-value, j)); side[j] = 1
            lo_n -= 1; hi_n += 1
        while lo_n < hi_n:
            prune()
            value, j = heapq.heappop(high)
            heapq.heappush(low, (-value, j)); side[j] = 0
            hi_n -= 1; lo_n += 1
        if i >= k - 1:
            prune()
            out.append(-low[0][0] if k % 2 else (-low[0][0] + high[0][0]) / 2)
    return out
```

## Complexity

Every number is pushed once and moved between the heaps a bounded number of times per step; every entry is popped at most once as stale. Total `O(n log n)` time and `O(n)` memory (the heaps may hold stale entries, but each entry is created once).

## Another way

Keep the window as a **sorted list**. When the window moves, delete the leaving number with `bisect_left` and insert the new one with `bisect.insort`. The median is read by index. Each step costs `O(k)` for the memory move, but that move is very fast (a few microseconds for `k = 20000`), so it passes the big test. It does not scale to windows of millions, where the heap (or a balanced tree) wins. A third way, "delayed deletion with a dictionary of counts per value" decides the side of the leaving number by comparing it with the top of the lower heap; it is shorter but easy to get wrong when the leaving value equals the top.
