## Hint 1

Think of a bucket with a small hole. Every request pours in one unit. Water leaks out at `rate` units per second. How full is the bucket when the next request arrives, if the last request left it at `excess` and `t - last` seconds passed? Can the bucket be less than empty?

## Hint 2

```text
first request: last = t; return "pass"
later: new_excess = max(0.0, excess - rate * (t - last) + 1.0)
       if new_excess > burst: return "503"          # state unchanged
       excess, last = new_excess, t
       return "pass" if new_excess == 0 or nodelay else "delayed"
```
