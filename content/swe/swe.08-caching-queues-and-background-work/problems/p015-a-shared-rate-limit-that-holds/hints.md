## Hint 1

What does `INCR` return? If it returns the **new** count, do you still need to read the count before deciding? And how can you give the key an expiry without a separate `EXPIRE` that a crash could skip?

## Hint 2

```text
key = f"rate:{user}:{int(now() // window)}"
r.set(key, 0, ex=window, nx=True)     # only the first request of the window creates it, with its TTL
return r.incr(key) <= limit
```
