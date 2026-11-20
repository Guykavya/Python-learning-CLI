## Approach

Let `f` be the largest count and `m` the number of letters that reach it.

- **Lower bound 1:** every task takes a unit, so at least `len(tasks)`.
- **Lower bound 2:** the copies of a most frequent letter are at least `n + 1` apart, so from the first to the last copy there are at least `(f - 1) * (n + 1)` units; and each of the `m` most frequent letters has its last copy in the final stretch, so add `m`.
- **The greedy schedule reaches the bigger bound.** Lay out `f` rows of `n + 1` cells; the last row keeps only `m` cells. Put the `m` most frequent letters in the first `m` columns (one copy per row). Fill the free cells of the first `f - 1` rows **column by column**, top to bottom, taking the other letters in order of **decreasing count**. A letter with `f - 1` copies then fills exactly one column, so its copies are one row (`n + 1` units) apart. Every later letter has at most `f - 2` copies, so even when it wraps from the bottom of one column to the top of the next, its two copies there are at least two rows apart, minus one column: `2(n + 1) - 1 >= n + 1` units. Empty cells become idle units. If the cells run out, make the rows longer: then nothing is idle, and the length is `len(tasks)`.

```python
from collections import Counter


def least_interval(tasks, n):
    if not tasks:
        return 0
    counts = Counter(tasks)
    f = max(counts.values())
    m = sum(1 for c in counts.values() if c == f)
    return max(len(tasks), (f - 1) * (n + 1) + m)
```

Check `["A"]*6 + B..G` with `n = 2`: `f = 6`, `m = 1`, `(6 - 1) * 3 + 1 = 16 > 12`. Answer 16: `A B C A D E A F G A . . A . . A`.

## Complexity

Counting is `O(len(tasks))`; the rest is over at most 26 letters. Space `O(1)` (26 counters).

## Another way

Simulate, greedily: at each time unit run the allowed letter with the **most copies left** (a max-heap of counts), and put a letter on hold for `n` units after it runs. This greedy is also optimal: running the letter with the most copies left first is what keeps the most frequent letter from being stuck at the end with forced idles. It is `O(total time * log 26)` and gives the actual schedule, not only its length.

```python
import heapq
from collections import Counter, deque


def least_interval(tasks, n):
    heap = [-c for c in Counter(tasks).values()]      # max-heap of counts left
    heapq.heapify(heap)
    waiting = deque()                                 # (time it is allowed again, -count left)
    time = 0
    while heap or waiting:
        if heap:
            c = heapq.heappop(heap) + 1               # run one copy (counts are negative)
            if c < 0:
                waiting.append((time + n + 1, c))
        time += 1
        if waiting and waiting[0][0] == time:
            heapq.heappush(heap, waiting.popleft()[1])
    return time
```
