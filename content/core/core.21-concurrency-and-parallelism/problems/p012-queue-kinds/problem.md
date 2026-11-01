# Trace: Queue, LifoQueue and PriorityQueue

The `queue` module has three thread-safe containers. They share the same methods (`put`,
`get`, `qsize`, `empty`, `full`, `put_nowait`, `get_nowait`) and differ only in **which item
`get` returns**:

| Class | `get()` returns |
|---|---|
| `Queue` | the **oldest** item (first in, first out) |
| `LifoQueue` | the **newest** item (last in, first out, like a stack) |
| `PriorityQueue` | the **smallest** item (by normal `<` comparison) |

Blocking rules: `put` on a full queue waits for a free place, `get` on an empty queue waits for
an item. The `_nowait` versions (and `get(timeout=...)`) do not wait forever: they raise
`queue.Full` or `queue.Empty` instead. `maxsize=0` (the default) means "no limit".

This program uses only the main thread. What does it print?

```python
import queue

q = queue.Queue()
for x in ["a", "b", "c"]:
    q.put(x)
print("Queue:", q.get(), q.get(), "left", q.qsize())

s = queue.LifoQueue()
for x in ["a", "b", "c"]:
    s.put(x)
print("LifoQueue:", s.get(), s.get(), "left", s.qsize())

p = queue.PriorityQueue()
for job in [(3, "low"), (1, "urgent"), (2, "normal"), (1, "also urgent")]:
    p.put(job)
order = []
while not p.empty():
    order.append(p.get()[1])
print("PriorityQueue:", order)

small = queue.Queue(maxsize=2)
small.put("x")
small.put("y")
print("full?", small.full(), "size", small.qsize())
try:
    small.put_nowait("z")
    print("z added")
except queue.Full:
    print("Full raised, size", small.qsize())
print("got", small.get_nowait())
small.put_nowait("z")
print("now", small.get(), small.get())

empty = queue.Queue()
try:
    empty.get_nowait()
except queue.Empty:
    print("Empty raised")
try:
    empty.get(timeout=0.01)
except queue.Empty:
    print("Empty after timeout, empty?", empty.empty())

unbounded = queue.Queue()
print("maxsize", unbounded.maxsize, "full?", unbounded.full())
```

**Example**: the first line is `Queue: a b left 1`. The two `get()` calls inside one `print`
run left to right, take the two oldest items, and one item (`c`) is left.

Write in `answer.txt` the lines the program prints, in order.
