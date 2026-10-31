## Hint 1

What must `RateLimiter` remember to answer "how many allowed calls happened in the last window"? A list
of times? A count? Which is easier to clean up when time moves on?

## Hint 2

In `allow`, read `now()` once. Throw away the remembered times that are `>= per_seconds` old, then
compare how many are left with `limit`. Record the new time only when you say `True`.

## Hint 3

```
now(): return time.monotonic()            # keep `import time`, do not `from time import ...`
allow(): t = now()
         self.calls = [c for c in self.calls if t - c < self.per_seconds]
         if len(self.calls) >= self.limit: return False
         self.calls.append(t); return True
```
