## Approach

Put a unique token in the lock, and delete only if the token is still yours, in one atomic step.

```python
import secrets


def new_token():
    return secrets.token_hex(16)


def acquire(r, name, token, ttl=10):
    return bool(r.set(f"lock:{name}", token, ex=ttl, nx=True))


def release(r, name, token):
    return r.delete_if_equals(f"lock:{name}", token) == 1
```

In real Redis, `delete_if_equals` is this Lua script, which Redis runs as one command:

```lua
if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end
```

## Cost

One round trip to acquire and one to release. The TTL is the trade-off: too short and a slow holder loses the lock while working (the story in the problem); too long and a crashed holder blocks everyone for that long.

## Another way

For correctness (money, stock), do not rely on the lock at all: use **fencing tokens** (an increasing number from `INCR`, checked by the resource), database transactions, unique constraints or conditional updates (`UPDATE ... WHERE version = ?`). For "only one scheduler runs the nightly job", an idempotent job with a dedupe key (chapter 14.3) is more robust than a lock.
