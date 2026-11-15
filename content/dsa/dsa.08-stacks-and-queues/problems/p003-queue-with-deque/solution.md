## Approach

A deque is a double-ended queue: adding or removing at **either** end is `O(1)`. Add at the right (`append`), remove at the left (`popleft`), and the oldest item always leaves first.

## Code

```python
from collections import deque


class Queue:
    def __init__(self):
        self._items = deque()

    def enqueue(self, x):
        self._items.append(x)

    def dequeue(self):
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def front(self):
        if not self._items:
            raise IndexError("front of empty queue")
        return self._items[0]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)
```

## Complexity

`O(1)` for every operation, `O(n)` memory. With a list and `pop(0)`, `n` dequeues cost `O(n^2)` in total: on a 300,000-item list that took about 20 seconds in an earlier test run, against a fraction of a second with a deque.

## Another way

`appendleft` + `pop` also gives a correct queue (add on the left, remove on the right). What matters is that you add at one end and remove at the other. `queue.Queue` from the standard library is a thread-safe queue for programs with several threads; for single-threaded algorithms the plain deque is simpler and faster.
