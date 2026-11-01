## Approach

Track each container's contents step by step.

| Step | Contents before | Operation | Printed / result |
|---|---|---|---|
| Queue | `[a, b, c]` | get, get (oldest first) | `a b`, 1 left |
| LifoQueue | `[a, b, c]` | get, get (newest first) | `c b`, 1 left |
| PriorityQueue | `(3,low) (1,urgent) (2,normal) (1,also urgent)` | get until empty, smallest first | ties on 1 are broken by the string: `"also urgent" < "urgent"` (`a` < `u`) |
| small | `[x, y]`, maxsize 2 | `full()` | `True`, size 2 |
| small | `[x, y]` | `put_nowait("z")` | raises `queue.Full`; `z added` is never printed; size still 2 |
| small | `[x, y]` | `get_nowait()` | `x`, leaves `[y]` |
| small | `[y]` | `put_nowait("z")`, then get, get | `y z` |
| empty | `[]` | `get_nowait()` | raises `queue.Empty` |
| empty | `[]` | `get(timeout=0.01)` | waits 0.01 s, raises `queue.Empty`; `empty()` is `True` |
| unbounded | `[]` | `maxsize`, `full()` | `0`, `False` (a limit of 0 means no limit) |

Lessons:

- A `PriorityQueue` compares **whole items**. With tuples, equal priorities are decided by the
  next element. If that element cannot be compared (two dicts, say), `put` raises `TypeError`.
  The usual fix is `(priority, counter, item)` with a running counter, which also keeps
  first-in-first-out order among equal priorities.
- `put_nowait` and `get_nowait` never wait; they raise. `get(timeout=...)` waits a little, then
  raises the same `queue.Empty`.
- In threaded code, `qsize()`, `empty()` and `full()` are only snapshots: another thread can
  change the queue right after you look. Here there is only one thread, so they are exact.

## Output

```text
Queue: a b left 1
LifoQueue: c b left 1
PriorityQueue: ['also urgent', 'urgent', 'normal', 'low']
full? True size 2
Full raised, size 2
got x
now y z
Empty raised
Empty after timeout, empty? True
maxsize 0 full? False
```
