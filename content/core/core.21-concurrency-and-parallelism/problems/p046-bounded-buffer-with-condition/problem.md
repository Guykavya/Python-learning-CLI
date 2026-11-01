# Build a bounded buffer with Condition

`queue.Queue(maxsize=n)` is built from one lock and **condition variables**. Building a small
version yourself is the best way to understand what "wait until there is room" really means
between threads.

Write `class BoundedBuffer(capacity)` **without** the `queue` module:

- `put(item, timeout=None)`: add `item` at the back. If the buffer already holds `capacity`
  items, **block** until a `get` makes room. With a `timeout` (seconds), give up after that long
  and raise `TimeoutError`.
- `get(timeout=None)`: remove and return the item at the front (first in, first out). If the
  buffer is empty, **block** until a `put` arrives; with a `timeout`, raise `TimeoutError` after
  that long.
- `len(buffer)`: the number of items in it now.
- `capacity < 1` raises `ValueError`.

Use a `collections.deque` for the items and **one** `threading.Condition` to protect it. A
Condition is a lock plus a waiting room:

```python
with cond:                                   # take the lock
    ok = cond.wait_for(lambda: <predicate>, timeout)   # sleep (lock released) until true
    ...change the state...
    cond.notify_all()                        # wake the sleepers so they re-check
```

`wait_for` returns the predicate's last value: `False` means it timed out.

**Example**

```python
buf = BoundedBuffer(2)
buf.put("a"); buf.put("b")
len(buf)                      # 2
buf.put("c", timeout=0.1)     # TimeoutError after 0.1 s: full
buf.get()                     # 'a'
buf.put("c")                  # room now
[buf.get(), buf.get()]        # ['b', 'c']
buf.get(timeout=0.1)          # TimeoutError after 0.1 s: empty

# Another thread calling buf.get() on an empty buffer waits until some thread puts an item.
```
