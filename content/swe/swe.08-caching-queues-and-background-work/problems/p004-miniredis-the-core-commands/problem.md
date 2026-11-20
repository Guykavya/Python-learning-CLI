# MiniRedis, the core commands

Chapter section 3.2 (MiniRedis: the same commands, in 100 lines). Redis is not installed in this course, so the chapter used a small stand-in with the **same method names and return values** as the `redis` Python package (created with `decode_responses=True`). Here you write the string part of it yourself. Afterwards, every Redis call you write in the other problems behaves the way you implemented it here.

## What to write

```python
class MiniRedis:
    def __init__(self, now=time.time): ...
    def set(self, key, value, ex=None, nx=False): ...   # True, or None when nx=True and the key exists
    def get(self, key): ...                             # the string, or None
    def delete(self, *keys): ...                        # how many of the keys existed (int)
    def exists(self, *keys): ...                        # how many of the keys exist (int)
    def incr(self, key, amount=1): ...                  # the new value (int)
    def expire(self, key, seconds): ...                 # True if the key exists, else False
    def ttl(self, key): ...                             # seconds left; -1 = no expiry; -2 = no such key
```

The rules, which match real Redis:

| Command | Rule |
|---|---|
| `set` | stores `str(value)`; **removes any old expiry** unless `ex` is given; `ex=10` expires the key 10 s from now; `nx=True` stores only if the key does **not** exist and returns `None` otherwise |
| `get` | a missing or expired key gives `None` |
| `incr` | a missing key counts as 0; the value is stored as a string; **an existing expiry is kept**; a value that is not an integer raises `ValueError` with a message starting `ERR value is not an integer` |
| `expire` | sets a new expiry on an existing key |
| `ttl` | `math.ceil` of the seconds left; `-1` for a key without expiry; `-2` for a missing (or expired) key |
| expiry | a key whose deadline is reached (`deadline <= now()`) is **gone** for every command. Remove it when a command touches it (lazy expiry); no background thread |

The clock is injected: `now` is a function returning seconds. Each command must be **atomic** when called from several threads: hold a `threading.RLock` for the whole command.

## Example

```python
clock = [1000.0]
r = MiniRedis(now=lambda: clock[0])
r.set("greeting", "hello", ex=30)     # True
r.get("greeting"), r.ttl("greeting")  # ('hello', 30)
r.set("greeting", "other", nx=True)   # None: the key already exists
r.incr("visits"), r.incr("visits", 10)  # (1, 11)
r.ttl("visits")                       # -1: no expiry
clock[0] += 31
r.get("greeting"), r.ttl("greeting")  # (None, -2)
```

### What MiniRedis does not do

Real Redis runs as a separate server, survives restarts if persistence is on, and has many more types (hashes, lists, sorted sets; the full chapter version has them) plus Lua scripts and transactions. It also deletes expired keys in a background sweep, not only lazily. The return values above are the ones `redis-py` gives with `decode_responses=True`.
