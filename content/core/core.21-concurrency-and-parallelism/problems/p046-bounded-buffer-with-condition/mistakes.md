- `while len(self._items) >= self.capacity: time.sleep(0.01)` (busy waiting). It wastes CPU,
  reacts late, and if it holds the lock while sleeping, no `get` can ever make room: deadlock.
- `if not full: cond.wait()` with `if` instead of a loop (or `wait_for`). After waking, another
  thread may already have filled the slot; you then append into a full buffer.
- Checking the length **outside** `with self._cond` and appending inside. Two threads both see
  "room for one" and both append.
- Using `notify()` with a single shared Condition. It can wake a thread of the wrong kind and
  leave the useful one asleep; the stress test then hangs until its join timeout.
- Forgetting to notify after `get`. Putters waiting for room are never woken.
- Calling `cond.wait()` or `notify_all()` without holding the lock: `RuntimeError: cannot
  wait on un-acquired lock`.
- Ignoring `wait_for`'s return value. After a timeout it returns `False`, and the code goes on
  to `popleft()` from an empty deque (`IndexError`) instead of raising `TimeoutError`.
- Using `list.pop(0)` for the front item: O(n) per get. `deque.popleft()` is O(1).
