## Hint 1

What two numbers does a bucket need to remember between calls? (The tokens it holds now, and the time of the last refill.) When must the refill happen: before or after you decide to allow the request? And what stops the bucket from growing past `capacity` after a long idle time?

## Hint 2

When the bucket is empty, how many tokens are missing for the next request, and how many seconds does that take at `rate` tokens per second? Which `math` function turns `1.5` into `2`? Why must a refusal never leave `0` as the answer?

## Hint 3

```text
__init__: tokens = capacity (a float), last = clock()
take():
    now = clock()
    tokens = min(capacity, tokens + (now - last) * rate);  last = now
    if tokens >= 1: tokens -= 1; return (True, 0)
    return (False, ceil((1 - tokens) / rate))

rate_limit(bucket): return a function that
    calls bucket.take(); on refusal raises HTTPException(429, ..., headers={"Retry-After": str(wait)})
```
