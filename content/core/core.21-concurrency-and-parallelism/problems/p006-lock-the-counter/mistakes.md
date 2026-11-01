- Locking only the write (`with lock: self._value = current + 1`). The read happened outside
  the lock, so two threads can still read the same old value.
- Creating the lock inside `increment()`. Every call gets its own new lock, so no thread ever
  waits for another.
- Making `_lock` a class attribute shared by all counters. It still gives correct totals, but
  unrelated counters now block each other.
- `self._lock.acquire()` without a matching `release()` in a `finally`. If anything raises
  between them, the lock stays taken and every later call hangs. Use `with`.
- Removing the `time.sleep(0)` because "it causes the bug". The gap is not the bug; it only
  makes the bug show. Real code has real work there.
- Thinking `self._value += 1` would be safe without a lock. It is still a read, an add and a
  write, and a thread switch can land between them.
