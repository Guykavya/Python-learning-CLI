## Hint 1

Why does the starter compute 8 times? Find the two separate steps that should have been one.
Now: if you wrap the **whole** method in one lock, same-key calls are fixed. Run the
different-keys test. Why is it slow now? What is the lock protecting while `compute()` sleeps?

## Hint 2

Use two kinds of lock:

- one small lock that guards the dictionaries (held for microseconds, never during `compute`);
- one lock **per key**, so threads for the same key queue up, but other keys do not.

```
with self._lock:
    if key in values: return values[key]
    key_lock = key_locks.setdefault(key, Lock())
with key_lock:
    ... check again: did another thread fill it while I waited?
    value = compute()
    store it (under self._lock)
    return value
```

## Hint 3

The second check inside `with key_lock` is not optional. Thread B waited on `key_lock`
while thread A computed. When B gets the lock, the value is already there; without the
check, B computes again. This pattern is called **double-checked locking**.

If `compute` raises inside `with key_lock`, `with` still releases the lock and nothing was
stored, so the next caller simply tries again.
