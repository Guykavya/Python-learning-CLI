## Approach

**The window.** A `deque` holds the times of the starts that still count. At time `now`, a
start `t` has expired when `t + per <= now`. Starts are appended in time order, so expired ones
are always at the left: `popleft()` them. If fewer than `rate` remain, record `now` and let the
caller in.

**The wait.** If the window is full, the earliest moment anything changes is when the oldest
start expires, `starts[0] + per`. Sleep exactly `starts[0] + per - now`, then loop and check
again (the `while True`). Sleeping a fixed 0.01 s and polling would also work, but it wakes up
hundreds of times for nothing and the waits are never exact.

**The lock.** Without it, three tasks waiting for the same slot all compute the same wake-up
time, all wake together, and (if the check and the `append` were separated by an `await`) could
all get in. More importantly, nobody guarantees *which* waiter gets the slot. `asyncio.Lock`
wakes waiters in FIFO order, and only the lock holder checks and sleeps; the others queue
behind it. So arrival order is kept and the window is checked by one task at a time.

The lock is held while sleeping. That is intended here: nobody behind the first waiter could
start earlier anyway.

**`__aexit__`** returns `False`: the limiter has nothing to undo (a start is a start, even if
the request then fails), and returning a true value would swallow the body's exception.

**Injected clock and sleep.** Real time makes tests slow and flaky. With a fake clock that
moves only when `sleep` is called, the test can say "the 4th start happened at exactly 1.0".

Trace for `rate=2, per=1.0` from the problem:

| now | deque before | action | deque after |
|---|---|---|---|
| 0.0 | `[]` | start | `[0.0]` |
| 0.5 | `[0.0]` | start | `[0.0, 0.5]` |
| 0.6 | `[0.0, 0.5]` | full, sleep 0.4 | |
| 1.0 | drop 0.0 | start | `[0.5, 1.0]` |
| 1.0 | `[0.5, 1.0]` | full, sleep 0.5 | |
| 1.5 | drop 0.5 | start | `[1.0, 1.5]` |

## Code

```python
import asyncio
import time
from collections import deque


class RateLimiter:
    def __init__(self, rate, per, clock=time.monotonic, sleep=asyncio.sleep):
        if rate < 1:
            raise ValueError("rate must be at least 1")
        if per <= 0:
            raise ValueError("per must be positive")
        self.rate = rate
        self.per = per
        self.clock = clock
        self.sleep = sleep
        self.starts = deque()
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        async with self._lock:
            while True:
                now = self.clock()
                while self.starts and self.starts[0] + self.per <= now:
                    self.starts.popleft()
                if len(self.starts) < self.rate:
                    self.starts.append(now)
                    return self
                await self.sleep(self.starts[0] + self.per - now)

    async def __aexit__(self, exc_type, exc, tb):
        return False
```

## Complexity

Each start is appended once and popped once, so entering is O(1) amortized. Memory O(rate):
the deque never holds more than `rate` times.

## Another way

A **token bucket**: keep a number of tokens (up to `rate`) that refills continuously at
`rate / per` tokens per second; each start takes one token, and if none is left you sleep until
one has refilled. It needs only two numbers (tokens, last refill time) instead of a deque, and
it allows short bursts while keeping the long-run average. Many real APIs describe their limits
this way. The sliding window above is stricter: never more than `rate` starts in *any* window
of length `per`.

`time.monotonic` (not `time.time`) is the right default clock: it never jumps backwards when
the system clock is corrected.
