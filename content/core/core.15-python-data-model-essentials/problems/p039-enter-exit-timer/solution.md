## Approach

`with` is a guaranteed set-up and clean-up. The timer's set-up is "note the start time"; its clean-up is "compute the elapsed time", which must happen even when the block fails, so it belongs in `__exit__`. `__exit__`'s return value decides whether the exception is swallowed; here it is not.

`elapsed` as a property hides whether the timer is still running.

## Code

```python
import time


class Timer:
    def __init__(self, clock=time.perf_counter):
        self.clock = clock
        self._start = None
        self._elapsed = 0.0
        self.running = False

    def __enter__(self):
        self._start = self.clock()
        self.running = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self._elapsed = self.clock() - self._start
        self.running = False
        return False

    @property
    def elapsed(self):
        if self.running:
            return self.clock() - self._start
        return self._elapsed
```

## Complexity

O(1) time and memory.

## Another way

With `contextlib.contextmanager`: a generator that records `start = clock()`, `yield`s, and then stores the result in a `finally`. That is shorter, but then you need somewhere to store the result (a mutable object or a class), so the class-based version is a good fit for a timer.
