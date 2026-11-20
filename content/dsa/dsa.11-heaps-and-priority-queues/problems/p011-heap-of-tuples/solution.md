## Approach

Python compares tuples left to right and stops at the first difference. An entry `(priority, counter, task)` is therefore decided by the priority; if the priorities are equal, by the counter; and the counter is unique, so the comparison never reaches the task. The counter also gives the first-in-first-out order among equal priorities for free.

## Code

```python
import heapq
import itertools


class TaskQueue:
    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def add(self, priority, task):
        heapq.heappush(self._heap, (priority, next(self._counter), task))

    def pop(self):
        _, _, task = heapq.heappop(self._heap)
        return task

    def __len__(self):
        return len(self._heap)
```

## Complexity

`O(log n)` for `add` and `pop`, `O(n)` memory (three references per entry instead of two).

## Another way

Make the task class itself comparable (`functools.total_ordering`, or `__lt__` that compares only the priority); then `(priority, task)` is enough, but you must be able to change the class of the tasks. A counter works for any task. If you want the **last** added task first among equal priorities (a stack-like order), use a counter that counts down (`itertools.count(0, -1)`).
