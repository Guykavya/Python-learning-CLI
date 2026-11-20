## Approach

Let Redis do the counting in one atomic command and create the key with its TTL in another atomic command:

```python
def allow(r, user, limit, window, now):
    key = f"rate:{user}:{int(now() // window)}"
    r.set(key, 0, ex=window, nx=True)
    return r.incr(key) <= limit
```

- `SET ... NX EX` creates the window key **with** its expiry in one step; later calls do nothing, so the expiry is the one from the first request.
- `INCR` returns the new count, so the decision uses a number no other worker can have seen. Two simultaneous requests at count 2 get 3 and 4: one allowed, one refused.
- If the process dies between the two commands, the key already has its TTL, so it cannot live for ever (the `INCR`-then-`EXPIRE` bug from the chapter).

## Cost

Two round trips per request (one in real Redis with a pipeline or a Lua script). O(1) memory per user per window.

## Another way

A **sliding-window log** (chapter 7.2) uses a sorted set of timestamps and is exact at window edges (a fixed window allows up to `2 x limit` requests across a boundary). Its check-then-add steps must be atomic too, which in real Redis means a Lua script. A **token bucket** gives smooth rates and bursts; it also needs one atomic script.
