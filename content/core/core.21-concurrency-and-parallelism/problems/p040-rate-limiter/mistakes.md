- Using `asyncio.Semaphore(rate)`. It limits requests **in flight**, not **starts per second**.
  Fast requests free their slots at once and the rate is not limited at all.
- A fixed window (`if second changed: count = 0`). It allows up to `2 * rate` starts within one
  `per` around the boundary, which is exactly what servers punish.
- Calling `time.monotonic()` and `asyncio.sleep()` directly instead of `self.clock()` and
  `self.sleep()`. The tests then wait in real time and the fake clock never moves.
- Sleeping a fixed `per` when the window is full. You wait too long (the oldest start may
  expire much sooner).
- Recording the start **before** waiting, or not checking the window again after sleeping.
  Several waiters then get in together.
- Creating the `asyncio.Lock` inside `__aenter__`. Every call gets its own lock and nothing is
  serialized.
- Using `time.sleep` in `__aenter__`. It freezes the whole event loop, so no other task can run
  while one waits.
- Removing expired starts with `<` instead of `<=`: then a start exactly `per` ago still counts
  and callers wait one extra cycle.
