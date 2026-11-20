## Hint 1

Every command starts with the same question: "is this key still alive?". Write one private helper, `_alive(key)`, that removes the key from both dictionaries if its deadline has passed and then returns whether the key is present. Call it first in every command.

## Hint 2

```text
_alive(key):
    deadline = expires.get(key)
    if deadline is not None and deadline <= now(): remove key from data and expires
    return key in data

set(key, value, ex, nx):    with lock:
    if nx and _alive(key): return None
    data[key] = str(value); expires.pop(key)        # a plain SET clears the old expiry
    if ex is not None: expires[key] = now() + ex
    return True

incr(key, amount):          with lock:
    current = data[key] if _alive(key) else "0"
    value = int(current) + amount   (ValueError -> "ERR value is not an integer or out of range")
    data[key] = str(value)           # do NOT touch expires: INCR keeps the TTL
    return value

ttl(key): -2 if not alive; -1 if no deadline; else ceil(deadline - now())
```
