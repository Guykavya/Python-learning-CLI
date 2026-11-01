# A sliding-window rate limiter

An API allows **at most 3 requests per second**. A semaphore cannot express that: it limits how
many requests are *in flight*, not how many *start* in a period. Three fast requests finish in
10 ms, free their slots, and the semaphore happily lets 3 more start in the same second.

Write `class RateLimiter` used as an async context manager:

```python
limiter = RateLimiter(rate=3, per=1.0)

async with limiter:          # waits here until starting is allowed
    await client.get(url)
```

Rules (a **sliding window**):

- Entering `async with limiter` records a *start* at the current time.
- At any moment, the starts in the last `per` seconds may number at most `rate`. A start at
  time `t` stops counting at time `t + per` exactly.
- If the window is full, entering **waits** (with `await`) until the oldest start in the window
  expires, then checks again.
- Waiters get in **in the order they arrived** (first come, first served).
- Leaving the block does nothing special, and an exception inside the block is **not**
  swallowed.
- `RateLimiter(rate, per, clock=time.monotonic, sleep=asyncio.sleep)`: always read the time with
  `self`'s `clock()` and wait with its `sleep(seconds)`. The tests pass a fake clock and a
  fake sleep that moves the fake clock forward, so they run instantly and are exact.
- `rate < 1` or `per <= 0` raises `ValueError`.

**Example** (`rate=2, per=1.0`, times from the fake clock)

```text
t=0.0   start #1                       window: [0.0]
t=0.5   start #2                       window: [0.0, 0.5]
t=0.6   wants to start: window full -> sleeps 0.4 s (until 0.0 + 1.0)
t=1.0   0.0 expired, start #3          window: [0.5, 1.0]
t=1.0   wants to start: window full -> sleeps 0.5 s
t=1.5   0.5 expired, start #4          window: [1.0, 1.5]
```

A *fixed* window ("reset the counter every whole second") would let #3 and #4 both start at
1.0, and in the worst case allows `2 * rate` starts within one `per` across a boundary.
