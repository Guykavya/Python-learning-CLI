## Hint 1

Without single flight, every request that arrives **before** the first load finishes also misses. How many requests arrive in the window from t = 0 up to (but not including) t = `load_ms`?

## Hint 2

Requests arrive at t = 0, gap, 2·gap, ... with gap = 1000 / rate. The misses are those with t < load_ms, so the count is `load_ms / gap` = `rate x load_ms / 1000` (when it divides exactly). With single flight the answer is always 1: the lock is set by the first request and every later request either waits or hits.

```text
line 1: gap 5 ms,  t = 0, 5, ..., 95  -> 20 loads
line 4: gap 1 ms,  t = 0 .. 249       -> 250 loads
```
