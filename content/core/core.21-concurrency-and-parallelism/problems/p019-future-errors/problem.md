# Trace: what a Future does with errors and cancel

A `Future` is a box for a result that is not ready yet. Remember these rules:

- `future.result()` waits, then returns the value, or **re-raises** the exception the job
  raised (in your thread), or raises `CancelledError` if the future was cancelled.
- `future.exception()` waits, then **returns** the exception object (or `None` if the job
  succeeded). It does not raise it.
- `future.cancel()` only works on a job that is **still waiting in the queue**. A running or
  finished job cannot be cancelled, and `cancel()` returns `False`.
- `executor.map(fn, items)` submits **all** items at once and returns an iterator right away.
  Exceptions come out of the iterator when you reach the failing item.

The pool below has **one** worker thread, so jobs run strictly one after another. The two
`Event`s make the order fixed: the main thread waits for `started` before it submits `q`,
so when `q` is submitted the only worker is busy inside `blocker()`.

What does this program print?

```python
import threading
from concurrent.futures import CancelledError, ThreadPoolExecutor


def work(x):
    if x == 3:
        raise ValueError(f"bad {x}")
    return x * 10


started = threading.Event()
gate = threading.Event()


def blocker():
    started.set()
    gate.wait()
    return "blocker done"


with ThreadPoolExecutor(max_workers=1) as ex:
    f1 = ex.submit(work, 1)
    print("f1 result:", f1.result())
    print("f1 exception:", f1.exception())

    f2 = ex.submit(work, 3)
    try:
        f2.result()
    except ValueError as e:
        print("f2 raised:", e)
    print("f2 exception:", repr(f2.exception()))
    print("f2 done:", f2.done())

    b = ex.submit(blocker)
    started.wait()                 # the only worker is now inside blocker()
    q = ex.submit(work, 2)         # waits in the queue behind blocker
    print("cancel q:", q.cancel())
    print("q cancelled:", q.cancelled(), "q done:", q.done())
    print("cancel b:", b.cancel())
    try:
        q.result()
    except CancelledError:
        print("q.result() raised CancelledError")
    gate.set()
    print("b result:", b.result())

    results = ex.map(work, [1, 2, 3, 4])
    print("map returned an iterator")
    try:
        for r in results:
            print("got", r)
    except ValueError as e:
        print("map raised:", e)

print("end")
```

**Example**: the first line is `f1 result: 10`. `work(1)` returns `1 * 10`, and `result()`
waits for it and returns it.

Write in `answer.txt` the lines the program prints, in order.
