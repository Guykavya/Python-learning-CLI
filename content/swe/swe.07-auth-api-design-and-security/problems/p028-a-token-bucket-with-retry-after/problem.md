# A token bucket with Retry-After

Chapter sections 11.2 and 11.4. A token bucket holds up to `capacity` tokens. Every request takes one token. Tokens come back at `rate` per second. A full bucket allows a short burst; after that only the steady rate gets through. When the bucket has no token, the API answers **429** and tells the client how long to wait in a **`Retry-After`** header.

Write two things in `solution.py`.

**1. `TokenBucket(capacity, rate, clock)`**

- `capacity`: the largest number of tokens (and the size of the largest burst). A new bucket starts **full**.
- `rate`: tokens added per second (it may be a fraction, `0.5` means one token every 2 seconds).
- `clock`: a function with no arguments that returns the time in seconds. **Never call `time.time()`.** The tests move a fake clock, so nothing sleeps.
- `take()` returns a tuple `(allowed, retry_after)`:
  - `(True, 0)` when a token was available (the token is used);
  - `(False, seconds)` when the bucket is empty. `seconds` is a whole number of seconds, **rounded up** (`math.ceil`), the time until one full token exists. It is never `0` for a refusal.
- Refill first: `tokens = min(capacity, tokens + elapsed * rate)`. A refused request must **not** use up anything.

**2. `rate_limit(bucket)`** returns a FastAPI dependency (a function you can put in `Depends(...)`). It calls `bucket.take()`. If the request is refused it raises `HTTPException(429, ...)` with the header `Retry-After` set to the number of seconds as text (`"2"`). If it is allowed it does nothing.

## Example

```text
b = TokenBucket(capacity=3, rate=0.5, clock=clock)      # one token every 2 seconds
clock = 0:   take() -> (True, 0)   (True, 0)   (True, 0)
clock = 0:   take() -> (False, 2)                       # empty; one token needs 2 s
clock = 1:   take() -> (False, 1)                       # half a token exists, 1 s to go
clock = 2:   take() -> (True, 0)                        # one token is back
```

Over HTTP the refused call looks like `429` with the header `Retry-After: 2`.

The tests import `TokenBucket` and `rate_limit`. Use rates that are exact in binary (`0.5`, `0.25`, `2.0`), as the tests do, so the sums are exact.
