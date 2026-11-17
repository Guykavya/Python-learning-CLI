## Approach

Greedy with a clock. At each time unit run, among the tasks that are **available**, the one with the **most copies left**. The task with most copies left is the bottleneck: it needs the longest chain of gaps, so it should be started as early as possible. A task that has just run is **cooling** for `n` units and cannot be chosen; it goes into a waiting queue with the time at which it is available again, and comes back to the heap then. If no task is available, the unit is idle (and the clock still ticks). The answer is the clock at the end.

Cooling tasks leave in the same order as they entered (a task run at time `t` returns at `t + n + 1`), so a plain FIFO queue is enough.

## Code

```python
import heapq
from collections import Counter, deque

def least_interval(tasks, n):
    heap = [-count for count in Counter(tasks).values()]
    heapq.heapify(heap)
    cooling = deque()                                    # (available_at, remaining as a negative number)
    time = 0
    while heap or cooling:
        time += 1
        while cooling and cooling[0][0] <= time:
            heapq.heappush(heap, cooling.popleft()[1])
        if heap:
            remaining = heapq.heappop(heap) + 1          # one copy is run now
            if remaining < 0:
                cooling.append((time + n + 1, remaining))
        # else: nothing is available: an idle unit
    return time
```

## Complexity

`O(T log a)` time where `T` is the answer and `a` the number of different kinds (at most 26 letters, so about `O(T)`), `O(a)` memory. `T` can be much bigger than the number of tasks, because of idle units.

## Another way

**A formula.** Let `m` be the largest number of copies of one kind and `k` the number of kinds that have exactly `m` copies. The `m - 1` gaps between the copies of a most frequent task must each be `n + 1` units wide, and the last block holds the `k` last copies: `(m - 1) * (n + 1) + k` units. If there are so many other tasks that they fill all idle slots (and more), no idle unit is needed and the answer is just `len(tasks)`:

```python
def least_interval(tasks, n):
    counts = Counter(tasks).values()
    m = max(counts, default=0)
    k = sum(1 for c in counts if c == m)
    return max(len(tasks), (m - 1) * (n + 1) + k)
```

It is `O(len(tasks))` and does not need a heap or a clock; the simulation shows **why** it is right, and the formula is quicker when `n` is huge.
