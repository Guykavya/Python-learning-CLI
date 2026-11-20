# A shared rate limit that holds

Chapter section 7.2 (shared rate limits). Several web workers share one Redis. A user may make `limit` requests per `window` seconds (a **fixed window**: the window number is `int(now() // window)`). The starter's version reads the count, compares, and writes it back:

```python
def allow(r, user, limit, window, now):
    key = f"rate:{user}:{int(now() // window)}"
    count = int(r.get(key) or 0)
    if count >= limit:
        return False
    r.set(key, count + 1, ex=window)
    return True
```

Two bugs:

1. **Read-modify-write across two commands** (p005): two workers at the limit both read `limit - 1` and both let the request through.
2. Every `set` **restarts** the expiry, so a user who keeps calling keeps the window key alive longer than the window.

## What to write

Rewrite `allow(r, user, limit, window, now) -> bool` so that:

- the key is `rate:<user>:<window number>`;
- the key is created **with its expiry in one command**: `r.set(key, 0, ex=window, nx=True)` (does nothing if it exists, so the first request's expiry stays);
- the count goes up with **`r.incr(key)`** (atomic; keeps the TTL), and the request is allowed if the new count is `<= limit`.

Note that a refused request still increments the counter. That is normal for this algorithm.

## Example

```python
clock = FakeClock(0)
r = MiniRedis(now=clock)
[allow(r, "ada", 3, 60, clock) for _ in range(4)]    # [True, True, True, False]
r.ttl("rate:ada:0")                                  # 60
clock.advance(60)
allow(r, "ada", 3, 60, clock)                        # True: a new window, key rate:ada:1
```

One test runs two workers **at the same instant** against a Redis whose `GET` is slow, with the count already at `limit - 1`. The read-then-write version lets both through; yours must let exactly one through.
