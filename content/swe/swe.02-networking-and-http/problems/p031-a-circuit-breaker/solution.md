## Approach

```python
class CircuitOpen(Exception):
    pass


class CircuitBreaker:
    def __init__(self, threshold, cooldown, clock):
        self.threshold = threshold
        self.cooldown = cooldown
        self.clock = clock
        self._failures = 0
        self._opened_at = None

    @property
    def state(self):
        if self._opened_at is None:
            return "closed"
        if self.clock() - self._opened_at >= self.cooldown:
            return "half-open"
        return "open"

    def call(self, fn, *args, **kwargs):
        state = self.state
        if state == "open":
            raise CircuitOpen("circuit is open: failing fast")
        try:
            result = fn(*args, **kwargs)
        except Exception:
            if state == "half-open":
                self._opened_at = self.clock()          # the trial failed: open again
            else:
                self._failures += 1
                if self._failures >= self.threshold:
                    self._opened_at = self.clock()
            raise
        self._failures = 0
        self._opened_at = None
        return result
```

The state is **derived**, not stored: `_opened_at` plus the clock say which of the three states we are in. This avoids a timer thread, and the half-open state appears exactly when the cooldown has passed. The breaker does not swallow errors: the caller still sees the original exception (and decides what to do), but after `threshold` failures it sees `CircuitOpen` instead, **without waiting** for a slow dead service, which is the point of failing fast.

Example: `threshold=2`. Two failures: `_failures` reaches 2, `_opened_at = t`. At `t + 5`: `state` is `open`; `call` raises `CircuitOpen`. At `t + 10`: `half-open`; a success sets `_opened_at = None`: closed.

## Complexity

`O(1)` per call.

## Another way

Production libraries (`pybreaker`, resilience4j) add a limit of one concurrent trial in half-open, a failure *rate* instead of a count, and metrics. The core is these three states.

## Why it matters

Without a breaker, every request waits for a timeout on a dead dependency, threads pile up and the whole system falls with it. A breaker turns "slow failure" into "fast failure".
