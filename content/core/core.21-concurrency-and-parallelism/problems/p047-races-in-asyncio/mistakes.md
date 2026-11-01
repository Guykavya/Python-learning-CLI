- "One thread means no races." Any `await` between reading shared state and writing it is a
  gap where other tasks run.
- Locking only the subtraction. The check is then outside the lock, all tasks pass it with the
  old balance, and the lock just makes them subtract one by one into the negative.
- Creating the lock inside `spend` (`async with asyncio.Lock():`). Every call has its own
  lock, so nothing is protected.
- One lock for all wallets (a class attribute or a module global). Correct, but wallet A's
  fraud check now blocks every other wallet.
- Using `threading.Lock` in async code. `acquire()` blocks the event loop thread; if another
  task holds it across an `await`, the whole program deadlocks.
- `await self._lock.acquire()` without a `try/finally` release. If the check raises, the lock
  stays taken and every later spend waits forever. `async with` handles it.
- Removing the `await self.check(...)` to "fix" the race. The fraud check is the business
  rule; the task is to make it safe, not to skip it.
