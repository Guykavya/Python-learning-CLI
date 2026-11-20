# The lock bug

Chapter section 7.3 (distributed locks, and why they are dangerous) and "Try it: spot the lock bug". A Redis lock is the key `lock:<name>`, created with `SET lock:<name> <token> NX EX <ttl>`. The starter releases it like this:

```python
def release(r, name, token):
    r.delete(f"lock:{name}")
```

Run the chapter's story: A takes the lock (10 s TTL). A is paused for 15 s (a long garbage collection), so the lock **expires**, and B takes it. A wakes up and calls `release` — and deletes **B's** lock. Now C walks in while B is still working: two holders at once.

## What to write

```python
def new_token() -> str: ...                       # a fresh random token: secrets.token_hex(16)
def acquire(r, name, token, ttl=10) -> bool: ...  # True if this token now holds the lock
def release(r, name, token) -> bool: ...          # True only if THIS token's lock was deleted
```

- `acquire` uses `r.set(f"lock:{name}", token, ex=ttl, nx=True)` and returns a real `bool`.
- `release` must delete the lock **only if it still holds this token**, and the check and the delete must be **one atomic step**. A `get` followed by a `delete` is two commands: another worker can take the lock in between. Real Redis does this with a tiny Lua script; the `r` you receive has the same thing as a method:

```python
r.delete_if_equals(key, value)    # deletes key only if its value == value; returns 1 or 0
```

## Example

```python
clock = FakeClock(0)
r = LockingRedis(now=clock)
acquire(r, "report", "A")        # True
clock.advance(15)                 # A's lock expired
acquire(r, "report", "B")        # True
release(r, "report", "A")        # False: it is B's lock now
acquire(r, "report", "C")        # False: B still holds it
```

### After it works

Even this safe release cannot stop a paused A from **writing** after its lock expired. Read the chapter's **fencing token** example: the protected resource rejects writes with an older token. A Redis lock is an efficiency tool, not a correctness guarantee.
