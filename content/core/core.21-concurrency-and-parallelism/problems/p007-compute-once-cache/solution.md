## Approach

The bug is **check-then-act**: "is it cached?" and "store it" are separate steps, and the slow
`compute()` sits between them, so every thread passes the check.

The obvious fix, one lock around the whole method, is correct but **serialises everything**:
while one thread computes user 1, a thread that wants user 2 waits for nothing.

So split the locking:

1. A small **guard lock** protects the dictionaries. It is held only for dictionary
   operations, never during `compute()`.
2. A **lock per key**, created on first use with `setdefault` (under the guard lock so two
   threads cannot create two different locks for one key).
3. The thread that gets the key lock **checks again**, because another thread may have stored
   the value while it waited. Only if it is still missing does it compute and store.

Different keys use different key locks, so they compute in parallel. Same-key threads queue on
one key lock: the first computes, the rest find the value on their second check.

## Code

```python
import threading


class OnceCache:
    def __init__(self):
        self._values = {}
        self._key_locks = {}
        self._lock = threading.Lock()

    def get(self, key, compute):
        with self._lock:
            if key in self._values:
                return self._values[key]
            key_lock = self._key_locks.setdefault(key, threading.Lock())

        with key_lock:
            with self._lock:
                if key in self._values:
                    return self._values[key]
            value = compute()
            with self._lock:
                self._values[key] = value
            return value
```

Note that the guard lock and a key lock are never taken in the opposite order (the guard is
always taken **inside** the key lock or alone), so there is no deadlock (p008).

## Complexity

A cached hit is one dictionary lookup under a lock: O(1). A miss costs one `compute` per key in
total, however many threads ask. Memory: one value and one small lock per key. (A real cache
would also limit its size and could drop key locks after the value is stored.)

## Another way

Store a `concurrent.futures.Future` per key instead of a lock. The first thread puts a new
`Future` into the dict and computes; everyone else finds the `Future` and calls
`future.result()`, which waits and then returns the value (or re-raises the error). This
also lets waiting threads see the first thread's exception, and is how many async caches work.

`functools.lru_cache` is thread-safe in the sense that it will not corrupt itself, but it does
**not** promise "compute once": two threads with the same new key can both call the function.
