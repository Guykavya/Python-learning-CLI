# Model `limit_req`

Chapter section 7.5 (rate limiting at the proxy) and the swe.07 rate limiter. The chapter's Nginx line is:

```nginx
limit_req_zone $binary_remote_addr zone=per_ip:10m rate=20r/s;
limit_req zone=per_ip burst=40 nodelay;      # allow bursts of 40 beyond 20/s; refuse the rest with 503
```

Nginx does not count requests per second in fixed windows. It uses a **leaky bucket**: the bucket drains at `rate` requests per second, each request adds one, and `burst` is how many requests may be waiting in the bucket at once. Write a small model of it, to see exactly which request gets refused.

## What to write

```python
class LimitReq:
    def __init__(self, rate_per_s: float, burst: int = 0, nodelay: bool = False): ...
    def allow(self, t: float) -> str: ...      # "pass", "delayed" or "503"
```

The model keeps two numbers, `excess` (how full the bucket is; starts at `0.0`) and `last` (the time of the last accepted request; none at first). `allow(t)` is called with the time `t` of each request, in seconds, and the times never go backwards (raise `ValueError` if one does).

1. The **first** request ever: remember `last = t`, answer `"pass"`.
2. Every later request: `new_excess = max(0.0, excess - rate_per_s * (t - last) + 1.0)`.
3. If `new_excess > burst`: the request is refused: answer `"503"` and **change nothing** (a refused request does not fill the bucket).
4. Otherwise accept it: `excess = new_excess`, `last = t`. Answer `"pass"` if `new_excess == 0` **or** `nodelay` is true; otherwise `"delayed"` (without `nodelay`, Nginx holds the request back until it fits the rate).

Raise `ValueError` if `rate_per_s <= 0` or `burst < 0`.

## Example

```python
lim = LimitReq(rate_per_s=1, burst=2)
[lim.allow(t) for t in (0, 0, 0, 0, 1, 1, 3)]
# ['pass', 'delayed', 'delayed', '503', 'delayed', '503', 'delayed']

lim = LimitReq(rate_per_s=1, burst=2, nodelay=True)
[lim.allow(t) for t in (0, 0, 0, 0, 1, 1, 3)]
# ['pass', 'pass', 'pass', '503', 'pass', '503', 'pass']
```

Follow the first list by hand: after the 3rd request `excess` is 2 (the bucket holds the burst); the 4th would make it 3 > 2, so it is refused and `excess` stays 2; at `t = 1` the bucket has drained by 1 and the new request adds 1 again: `2 - 1 + 1 = 2`, allowed; a second request at `t = 1` would need 3: refused.

The tests use times that are exact in binary floating point (0.25, 0.5, whole numbers), so plain `==` on the results is safe. This is a **model**: real Nginx works in milliseconds and also reports how long to delay a request, but the pass/delay/reject pattern is the same.
