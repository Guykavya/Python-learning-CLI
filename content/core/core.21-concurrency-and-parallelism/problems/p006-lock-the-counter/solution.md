## Approach

The race is a **read-modify-write**: read `_value`, do something, write `current + 1`. If two
threads both read 10 before either writes, both write 11 and one increment is lost. The three
lines are a **critical section**: only one thread may be inside at a time.

A `threading.Lock` gives exactly that. `with self._lock:` waits until the lock is free, takes
it, runs the block, and releases it on the way out (also when an exception is raised). While
thread A holds it, thread B waits at the `with` line, so B always reads the value **after** A
wrote it.

The lock lives in `__init__`, one per counter. A lock created inside `increment` would be a new
lock on every call and protect nothing.

For `value`, reading a single attribute is already safe in CPython, but taking the lock there
too costs little and keeps the rule simple: "every access to `_value` holds `_lock`". That rule
keeps working if `value` ever grows into several steps.

## Code

```python
import threading
import time


class Counter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            current = self._value
            time.sleep(0)
            self._value = current + 1

    @property
    def value(self):
        with self._lock:
            return self._value
```

## Complexity

O(1) per call. The lock makes increments run **one at a time**, so this part does not run in
parallel any more. Keep critical sections short: lock the shared update, not the slow work
around it.

## Another way

`itertools.count()` with `next()` is effectively atomic in CPython, and some people use it as a
lock-free counter. It depends on an implementation detail, so a `Lock` is the clear and
portable choice. If threads only need to report totals at the end, a better design is no
sharing at all: each thread counts locally and the main thread adds the totals after `join()`.
