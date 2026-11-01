## Approach

Walk the program top to bottom. Every `print` runs in the main thread, and the single worker
plus the two `Event`s fix the order of everything else, so the output is the same every run.

| Step | What happens | State | Printed |
|---|---|---|---|
| `f1 = submit(work, 1)` | worker runs `work(1)` | f1 finished, value 10 | |
| `f1.result()` | waits, returns the value | | `f1 result: 10` |
| `f1.exception()` | job succeeded, so **returns** `None` | | `f1 exception: None` |
| `f2 = submit(work, 3)` | `work(3)` raises inside the worker | f2 finished with `ValueError('bad 3')` | |
| `f2.result()` | **re-raises** the stored exception in the main thread | caught by `except` | `f2 raised: bad 3` |
| `repr(f2.exception())` | **returns** the exception object, no raise | | `f2 exception: ValueError('bad 3')` |
| `f2.done()` | failing still counts as done | | `f2 done: True` |
| `b = submit(blocker)`, `started.wait()` | worker is now inside `blocker`, stuck on `gate.wait()` | b RUNNING | |
| `q = submit(work, 2)` | no free worker, so q waits in the queue | q PENDING | |
| `q.cancel()` | pending, so it can be cancelled | q CANCELLED | `cancel q: True` |
| `q.cancelled()`, `q.done()` | a cancelled future is also done | | `q cancelled: True q done: True` |
| `b.cancel()` | b is running; Python cannot stop a running thread | b still RUNNING | `cancel b: False` |
| `q.result()` | cancelled future raises `CancelledError` | | `q.result() raised CancelledError` |
| `gate.set()`, `b.result()` | blocker returns; the worker later skips the cancelled q | b finished | `b result: blocker done` |
| `results = ex.map(...)` | submits 4 jobs, returns an iterator **immediately** | | `map returned an iterator` |
| 1st `next` | result of `work(1)` | | `got 10` |
| 2nd `next` | result of `work(2)` | | `got 20` |
| 3rd `next` | `work(3)` failed, the iterator re-raises | loop ends in `except` | `map raised: bad 3` |
| `with` ends | `shutdown(wait=True)` waits for `work(4)`, whose result nobody reads | | |
| last line | | | `end` |

Lessons:

- An exception in a pool job is **not lost and not printed**: it waits in the future until
  someone calls `result()` (raises) or `exception()` (returns). If nobody asks, it is silently
  dropped, which is a common reason for "my thread job failed and I saw nothing".
- `cancel()` is a request to **not start** a job. It cannot interrupt one that is running.
- `executor.map` raises lazily, at the failing item, and the items after it are lost even
  though they ran.

## Output

```text
f1 result: 10
f1 exception: None
f2 raised: bad 3
f2 exception: ValueError('bad 3')
f2 done: True
cancel q: True
q cancelled: True q done: True
cancel b: False
q.result() raised CancelledError
b result: blocker done
map returned an iterator
got 10
got 20
map raised: bad 3
end
```

## Complexity

Not relevant for a trace; the program does a constant amount of work.

## Another way

To keep going after a failing item instead of losing the rest of `map`, submit each item
yourself and call `fut.exception()` (or wrap `fut.result()` in `try`) for every future. That
is exactly what `gather(..., return_exceptions=True)` does for asyncio.
