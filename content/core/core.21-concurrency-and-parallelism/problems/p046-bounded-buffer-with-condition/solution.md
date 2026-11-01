## Approach

A `threading.Condition` combines a lock with a waiting room:

- `with cond:` takes the lock, so the check and the change happen as one step that no other
  thread can split.
- `cond.wait_for(predicate, timeout)` checks `predicate()`. If it is false, it **releases the
  lock** and sleeps until notified (or the timeout passes), then re-takes the lock and checks
  again. It returns the predicate's final value, so `False` means "timed out".
- `cond.notify_all()` wakes every sleeping thread. Each one re-checks its own predicate, and
  those for which it is still false go back to sleep.

Why `wait_for` with a predicate, not a single `wait()` and an `if`? A woken thread is not
guaranteed that the condition still holds: another thread may have taken the item first, and
threads can even wake *spuriously*. Re-checking in a loop is the only correct pattern;
`wait_for` is that loop, written for you, and it also handles the remaining timeout.

Why `notify_all()`, not `notify()`? Putters and getters share **one** Condition. `notify()`
wakes a single thread, possibly one of the wrong kind: a `get` removes an item and wakes another
*getter*, which finds the buffer still empty and sleeps again, while the putter that could use
the free room sleeps on. With enough threads this ends in everyone asleep. (Two Conditions on
one shared lock, `not_full` and `not_empty`, is how `queue.Queue` avoids waking everyone; it
can then safely use `notify()`.)

## Code

```python
import threading
from collections import deque


class BoundedBuffer:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._items = deque()
        self._cond = threading.Condition()

    def put(self, item, timeout=None):
        with self._cond:
            if not self._cond.wait_for(lambda: len(self._items) < self.capacity, timeout):
                raise TimeoutError("buffer is full")
            self._items.append(item)
            self._cond.notify_all()

    def get(self, timeout=None):
        with self._cond:
            if not self._cond.wait_for(lambda: len(self._items) > 0, timeout):
                raise TimeoutError("buffer is empty")
            item = self._items.popleft()
            self._cond.notify_all()
            return item

    def __len__(self):
        with self._cond:
            return len(self._items)
```

## Complexity

`put` and `get` are O(1) plus waiting (deque append and popleft are O(1)). `notify_all` wakes
every waiter, so with w waiting threads each change costs O(w) wake-ups; the two-condition
version reduces that.

## Another way

```python
self._lock = threading.Lock()
self._not_full = threading.Condition(self._lock)
self._not_empty = threading.Condition(self._lock)
# put: wait_for on _not_full, append, _not_empty.notify()
# get: wait_for on _not_empty, popleft, _not_full.notify()
```

Both Conditions share one lock, so the state is still protected by a single lock, but each
change wakes exactly one thread of the kind that can use it. This is how the standard library's
`queue.Queue` is written; open `queue.py` and compare.
