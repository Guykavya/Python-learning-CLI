# The boundary burst

Chapter section 11.2 and "Try it: the boundary burst". Three rate limiters guard the same API: at most **5 requests per 10 seconds**. The program below sends 11 requests at fixed times through all three and prints what each limiter answers. Trace it by hand and write the output.

- `FixedWindow` counts requests in clock-aligned windows (seconds 0 to 10, 10 to 20, ...). Careful: the window is chosen from the clock, not from the first request.
- `SlidingWindowLog` removes times that are `<= now - 10`, then allows if fewer than 5 remain.
- `TokenBucket(5, 0.5, now)` starts with 5 tokens, refills 0.5 token per second (never above 5), and needs 1 whole token per request. It was created at time 0.0.

```python
from collections import deque


class FixedWindow:
    def __init__(self, limit, window, now):
        self.limit, self.window, self.now = limit, window, now
        self.slot, self.count = None, 0

    def allow(self):
        slot = int(self.now() // self.window)
        if slot != self.slot:
            self.slot, self.count = slot, 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False


class SlidingWindowLog:
    def __init__(self, limit, window, now):
        self.limit, self.window, self.now = limit, window, now
        self.times = deque()

    def allow(self):
        t = self.now()
        while self.times and self.times[0] <= t - self.window:
            self.times.popleft()
        if len(self.times) < self.limit:
            self.times.append(t)
            return True
        return False


class TokenBucket:
    def __init__(self, capacity, rate, now):
        self.capacity, self.rate, self.now = capacity, rate, now
        self.tokens, self.last = float(capacity), now()

    def allow(self):
        t = self.now()
        self.tokens = min(self.capacity, self.tokens + (t - self.last) * self.rate)
        self.last = t
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


clock = [0.0]
now = lambda: clock[0]
limiters = [FixedWindow(5, 10, now), SlidingWindowLog(5, 10, now), TokenBucket(5, 0.5, now)]
totals = [0, 0, 0]
for t in [0.0, 2.0, 4.0, 9.0, 9.5, 9.9, 10.1, 10.2, 10.5, 12.0, 14.0]:
    clock[0] = t
    answers = [lim.allow() for lim in limiters]
    for i, ok in enumerate(answers):
        totals[i] += ok
    words = ["yes" if ok else "no" for ok in answers]
    print(f"t={t} fixed={words[0]} sliding={words[1]} bucket={words[2]}")
print(f"allowed: fixed={totals[0]} sliding={totals[1]} bucket={totals[2]}")
```

Write your answer in `answer.txt`: 12 lines in the format of the `print` calls, 11 lines `t=... fixed=yes|no sliding=yes|no bucket=yes|no` and the last line `allowed: fixed=N sliding=N bucket=N`. Use only the words `yes` and `no`. Do not run it.

## Example

The first request, at `t=0.0`, finds every limiter empty of history, so all three allow it:

```text
t=0.0 fixed=yes sliding=yes bucket=yes
```

## After you answer

1. Count the `yes` answers of each limiter in the 10 seconds after `t=4.0` (times above 4.0, up to and including 14.0). Which limiter broke the promise "5 per 10 seconds" the most, and why?
2. The token bucket said `yes` at `t=9.9` while the other two said `no`. What does that tell you about the meaning of `capacity` and `rate` compared with "5 per 10 seconds"?
3. Which limiter would you use for a login endpoint, and which for a public read-only API? Explain in one sentence each.
