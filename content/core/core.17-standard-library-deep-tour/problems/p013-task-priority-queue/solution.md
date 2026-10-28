## Approach

`heapq` compares whole entries with `<`. A tuple compares its first fields; only if they are
equal does it look at the second, and so on. So an entry `(priority, count, task)`:

- orders by `priority` first;
- on a tie, by `count`, which grows by one on every push, so the earlier push wins (FIFO);
- never reaches `task`, because two counts are never equal. The task can be anything: a dict,
  `None`, an object without `<`.

`heap[0]` is always the smallest entry, so `peek` is O(1). `pop` and `push` are O(log n).

## Code

```python
import heapq
import itertools


class TaskQueue:
    def __init__(self) -> None:
        self._heap: list[tuple[int, int, object]] = []
        self._counter = itertools.count()

    def push(self, task, priority: int) -> None:
        heapq.heappush(self._heap, (priority, next(self._counter), task))

    def pop(self):
        if not self._heap:
            raise IndexError("pop from an empty TaskQueue")
        return heapq.heappop(self._heap)[2]

    def peek(self):
        if not self._heap:
            raise IndexError("peek at an empty TaskQueue")
        return self._heap[0][2]

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return len(self._heap) > 0
```

## Complexity

`push` and `pop`: O(log n). `peek`, `len`: O(1). Memory O(n).

## Another way

`queue.PriorityQueue` wraps the same heap with locks for use between threads; it has the
same tie problem, so you still push `(priority, count, item)`. Another option is a `@dataclass(order=True)`
entry with `item: object = field(compare=False)`, which tells the comparison to skip the item;
you still need the counter for FIFO order. For a max-priority queue, push `-priority`.
